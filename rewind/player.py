"""Replayer for navigating through recorded traces."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from rewind.storage import TraceStorage
from rewind.exceptions import FrameNotFoundError, ReplayError


@dataclass
class FrameInfo:
    """Information about a recorded frame."""
    index: int
    line_no: int
    filename: str
    function_name: str
    timestamp: float
    locals: Dict[str, Any]


class Player:
    """Navigate through recorded execution traces.

    Usage:
        player = Player("trace.db")
        frame = player.goto_frame(10)
        diff = player.diff_frames(5, 10)
    """

    def __init__(self, trace_path: str):
        self.trace_path = Path(trace_path)
        self.storage = TraceStorage(self.trace_path)
        self.storage.open()
        self._frame_cache: Dict[int, FrameInfo] = {}
        self._frame_list: Optional[List[Tuple[int, int, str, str, float]]] = None

    def close(self) -> None:
        """Close the trace database."""
        self.storage.close()

    @property
    def frame_count(self) -> int:
        """Total number of frames in trace."""
        return self.storage.get_frame_count()

    def _load_frame_list(self) -> List[Tuple[int, int, str, str, float]]:
        """Load all frame metadata."""
        if self._frame_list is None:
            self._frame_list = self.storage.get_all_frames()
        return self._frame_list

    def get_frame(self, index: int) -> FrameInfo:
        """Get frame by index."""
        if index < 0 or index >= self.frame_count:
            raise FrameNotFoundError(
                f"Frame {index} not found. Valid range: 0-{self.frame_count - 1}"
            )

        if index in self._frame_cache:
            return self._frame_cache[index]

        frame_id, line_no, filename, func_name, locals_dict, timestamp = \
            self.storage.get_frame(index)

        frame_info = FrameInfo(
            index=index,
            line_no=line_no,
            filename=filename,
            function_name=func_name,
            timestamp=timestamp,
            locals=locals_dict,
        )

        self._frame_cache[index] = frame_info
        return frame_info

    def goto_frame(self, index: int) -> FrameInfo:
        """Navigate to a specific frame (alias for get_frame)."""
        return self.get_frame(index)

    def diff_frames(self, index_a: int, index_b: int) -> Dict[str, Any]:
        """Compare two frames and return differences.

        Returns:
            Dictionary with 'added', 'removed', 'modified', 'unchanged' keys.
        """
        frame_a = self.get_frame(index_a)
        frame_b = self.get_frame(index_b)

        locals_a = frame_a.locals
        locals_b = frame_b.locals

        keys_a = set(locals_a.keys())
        keys_b = set(locals_b.keys())

        added = keys_b - keys_a
        removed = keys_a - keys_b
        common = keys_a & keys_b

        modified = {}
        unchanged = []

        for key in common:
            if locals_a[key] != locals_b[key]:
                modified[key] = {
                    'before': locals_a[key],
                    'after': locals_b[key],
                }
            else:
                unchanged.append(key)

        return {
            'added': list(added),
            'removed': list(removed),
            'modified': modified,
            'unchanged': unchanged,
        }

    def find_frame_by_line(self, filename: str, line_no: int) -> List[int]:
        """Find all frame indices matching a specific file and line."""
        frames = self._load_frame_list()
        matches = []

        for idx, (frame_idx, line, filepath, _, _) in enumerate(frames):
            if filepath.endswith(filename) and line == line_no:
                matches.append(frame_idx)

        return matches

    def search_variable(self, var_name: str) -> List[Tuple[int, Any]]:
        """Search for a variable across all frames.

        Returns:
            List of (frame_index, value) tuples.
        """
        results = []
        frames = self._load_frame_list()

        for frame_idx, _, _, _, _ in frames:
            try:
                frame = self.get_frame(frame_idx)
                if var_name in frame.locals:
                    results.append((frame_idx, frame.locals[var_name]))
            except Exception:
                continue

        return results

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()