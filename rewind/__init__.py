"""Rewind - Time-travel debugging for Python.

Rewind lets you record program execution and travel back in time
to inspect variables, fix bugs, and understand failures.
"""

__version__ = "0.1.0"
__author__ = "Rewind Contributors"
__license__ = "MIT"

from rewind.recorder import Recorder
from rewind.player import Player
from rewind.exceptions import RewindError, RecordingError, ReplayError

__all__ = [
    "Recorder",
    "Player",
    "RewindError",
    "RecordingError",
    "ReplayError",
]