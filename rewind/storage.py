"""Storage layer for trace files using SQLite."""

import sqlite3
import pickle
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from rewind.exceptions import RecordingError, TraceCorruptedError


class TraceStorage:
    """Handles reading/writing trace data to SQLite."""

    SCHEMA_VERSION = 1

    def __init__(self, path: Path):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None

    def create(self) -> None:
        """Create a new trace database."""
        self.conn = sqlite3.connect(str(self.path))
        self._init_schema()

    def open(self) -> None:
        """Open existing trace database."""
        if not self.path.exists():
            raise TraceCorruptedError(f"Trace file not found: {self.path}")

        self.conn = sqlite3.connect(str(self.path))
        self._verify_schema()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def _init_schema(self) -> None:
        """Initialize database schema."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS frames (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frame_index INTEGER NOT NULL,
                    line_no INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    locals_blob BLOB NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_frame_index
                ON frames(frame_index)
            """)

            self.conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_filename
                ON frames(filename)
            """)

            self.conn.execute("""
                INSERT INTO metadata (key, value)
                VALUES ('schema_version', ?)
            """, (str(self.SCHEMA_VERSION),))

            self.conn.execute("""
                INSERT INTO metadata (key, value)
                VALUES ('created_at', ?)
            """, (datetime.now().isoformat(),))

    def _verify_schema(self) -> None:
        """Verify database schema version."""
        cursor = self.conn.execute(
            "SELECT value FROM metadata WHERE key = 'schema_version'"
        )
        row = cursor.fetchone()

        if not row or int(row[0]) != self.SCHEMA_VERSION:
            raise TraceCorruptedError(
                f"Schema version mismatch. Expected {self.SCHEMA_VERSION}, "
                f"got {row[0] if row else 'none'}"
            )

    def save_frame(
        self,
        frame_index: int,
        line_no: int,
        filename: str,
        function_name: str,
        locals_dict: Dict[str, Any],
        timestamp: float,
    ) -> int:
        """Save a frame snapshot to database.

        Returns:
            The frame ID in database.
        """
        compressed = zlib.compress(pickle.dumps(locals_dict))

        with self.conn:
            cursor = self.conn.execute("""
                INSERT INTO frames
                (frame_index, line_no, filename, function_name, locals_blob, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (frame_index, line_no, filename, function_name, compressed, timestamp))

        return cursor.lastrowid

    def get_frame(self, frame_index: int) -> Tuple[int, int, str, str, Dict[str, Any], float]:
        """Retrieve a frame by its index.

        Returns:
            Tuple of (frame_id, line_no, filename, function_name, locals_dict, timestamp)
        """
        cursor = self.conn.execute("""
            SELECT id, line_no, filename, function_name, locals_blob, timestamp
            FROM frames
            WHERE frame_index = ?
        """, (frame_index,))

        row = cursor.fetchone()
        if not row:
            raise TraceCorruptedError(f"Frame {frame_index} not found")

        frame_id, line_no, filename, func_name, compressed, timestamp = row
        locals_dict = pickle.loads(zlib.decompress(compressed))

        return (frame_id, line_no, filename, func_name, locals_dict, timestamp)

    def get_all_frames(self) -> List[Tuple[int, int, str, str, float]]:
        """Get list of all frames (without locals to save memory).

        Returns:
            List of (frame_index, line_no, filename, function_name, timestamp)
        """
        cursor = self.conn.execute("""
            SELECT frame_index, line_no, filename, function_name, timestamp
            FROM frames
            ORDER BY frame_index
        """)

        return cursor.fetchall()

    def get_frame_count(self) -> int:
        """Get total number of recorded frames."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM frames")
        return cursor.fetchone()[0]

    def __enter__(self):
        if not self.conn:
            self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()