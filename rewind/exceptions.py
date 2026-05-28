"""Custom exceptions for Rewind."""


class RewindError(Exception):
    """Base exception for all Rewind errors."""
    pass


class RecordingError(RewindError):
    """Raised when recording fails."""
    pass


class ReplayError(RewindError):
    """Raised when replay fails."""
    pass


class TraceCorruptedError(ReplayError):
    """Raised when trace file is corrupted."""
    pass


class FrameNotFoundError(ReplayError):
    """Raised when requested frame doesn't exist."""
    pass