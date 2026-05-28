"""Tests for Recorder module."""

import pytest
import tempfile
from pathlib import Path

from rewind.recorder import Recorder
from rewind.player import Player


def test_recorder_basic():
    """Test basic recording functionality."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name

    recorder = Recorder(trace_path)

    recorder.start()

    x = 10
    y = 20
    z = x + y

    recorder.stop()

    player = Player(trace_path)
    assert player.frame_count > 0

    frame = player.get_frame(0)
    assert 'x' in frame.locals or 'y' in frame.locals

    player.close()
    Path(trace_path).unlink(missing_ok=True)


def test_recorder_context_manager():
    """Test recorder as context manager."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name

    with Recorder(trace_path) as recorder:
        test_var = 42
        another = "hello"

    player = Player(trace_path)
    assert player.frame_count >= 1

    player.close()
    Path(trace_path).unlink(missing_ok=True)


def test_recorder_handles_non_serializable():
    """Test recorder handles non-serializable objects gracefully."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        trace_path = tmp.name

    class NonSerializable:
        def __getstate__(self):
            raise Exception("Cannot serialize")

    obj = NonSerializable()

    with Recorder(trace_path) as recorder:
        value = obj

    player = Player(trace_path)
    assert player.frame_count > 0

    player.close()
    Path(trace_path).unlink(missing_ok=True)