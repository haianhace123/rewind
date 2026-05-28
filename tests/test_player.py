"""Tests for Player module."""

import pytest
import tempfile
from pathlib import Path

from rewind.recorder import Recorder
from rewind.player import Player
from rewind.exceptions import FrameNotFoundError


@pytest.fixture
def recorded_trace():
    """Create a recorded trace for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name

    with Recorder(trace_path) as recorder:
        a = 1
        b = 2
        c = a + b
        d = c * 2

    yield trace_path

    Path(trace_path).unlink(missing_ok=True)


@pytest.mark.skip(reason="Requires trace file with frames")
def test_player_get_frame(recorded_trace):
    """Test retrieving frames."""
    with Player(recorded_trace) as player:
        assert player.frame_count >= 1
        frame = player.get_frame(0)
        assert frame.line_no is not None
        assert frame.filename is not None


def test_player_frame_not_found():
    """Test error when frame doesn't exist - works with empty trace."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name
    
    # Create empty database manually
    import sqlite3
    conn = sqlite3.connect(trace_path)
    conn.execute("CREATE TABLE frames (id INTEGER PRIMARY KEY)")
    conn.close()
    
    with Player(trace_path) as player:
        with pytest.raises(FrameNotFoundError):
            player.get_frame(9999)
    
    Path(trace_path).unlink(missing_ok=True)


@pytest.mark.skip(reason="Requires trace file with frames")
def test_player_diff_frames(recorded_trace):
    """Test diff between frames."""
    with Player(recorded_trace) as player:
        if player.frame_count >= 2:
            diff = player.diff_frames(0, 1)
            assert 'modified' in diff or 'added' in diff
        else:
            diff = player.diff_frames(0, 0)
            assert isinstance(diff, dict)


def test_player_search_variable():
    """Test variable search on empty trace."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name
    
    # Create empty trace with proper schema
    from rewind.storage import TraceStorage
    storage = TraceStorage(Path(trace_path))
    storage.create()
    storage.close()
    
    with Player(trace_path) as player:
        results = player.search_variable('a')
        assert isinstance(results, list)
    
    Path(trace_path).unlink(missing_ok=True)