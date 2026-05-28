"""Execution recorder that captures program state at each line."""

import sys
import threading
from pathlib import Path
from typing import Any, Dict, Optional, Set, Callable
from datetime import datetime
import inspect
import pickle

from rewind.storage import TraceStorage
from rewind.exceptions import RecordingError


class Recorder:
    """Records Python execution with state snapshots at each line.

    Usage:
        recorder = Recorder("trace.db")
        recorder.start()
        # your code here
        recorder.stop()
        recorder.save()
    """

    def __init__(self, trace_path: str = "trace.db"):
        self.trace_path = Path(trace_path)
        self.storage: Optional[TraceStorage] = None
        self.frame_counter = 0
        self.original_trace_function: Optional[Callable] = None
        self._recording = False
        self._skip_functions: Set[str] = {
            "<module>",
            "__enter__",
            "__exit__",
            "__getattr__",
            "__setattr__",
        }

    def start(self) -> None:
        """Start recording execution."""
        if self._recording:
            raise RecordingError("Recorder is already running")

        try:
            self.storage = TraceStorage(self.trace_path)
            self.storage.create()
        except Exception as e:
            raise RecordingError(f"Failed to create trace storage: {e}")

        self.frame_counter = 0
        self._recording = True
        self.original_trace_function = sys.gettrace()
        sys.settrace(self._trace_callback)

    def stop(self) -> None:
        """Stop recording execution."""
        if not self._recording:
            return

        sys.settrace(self.original_trace_function)
        self._recording = False

        if self.storage:
            self.storage.close()
            self.storage = None

    def save(self) -> None:
        """Save the trace to disk."""
        if self.storage:
            self.storage.close()
            self.storage = None

    def _should_skip_frame(self, frame) -> bool:
        """Determine if a frame should be skipped."""
        func_name = frame.f_code.co_name
        filename = frame.f_code.co_filename

        if func_name in self._skip_functions:
            return True

        if "rewind" in filename and "recorder" in filename:
            return True

        if filename == "<stdin>":
            return False

        return False

    def _trace_callback(self, frame, event, arg):
        """Callback invoked by Python's tracing system."""
        if not self._recording:
            return self._trace_callback

        if event == 'line':
            if self._should_skip_frame(frame):
                return self._trace_callback

            self._record_frame(frame)

        return self._trace_callback

    def _record_frame(self, frame) -> None:
        """Capture and store the current frame state."""
        safe_locals = self._sanitize_locals(frame.f_locals)

        timestamp = datetime.now().timestamp()

        self.storage.save_frame(
            frame_index=self.frame_counter,
            line_no=frame.f_lineno,
            filename=frame.f_code.co_filename,
            function_name=frame.f_code.co_name,
            locals_dict=safe_locals,
            timestamp=timestamp,
        )

        self.frame_counter += 1

    def _sanitize_locals(self, locals_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Remove non-serializable objects from locals dictionary."""
        safe_dict = {}

        for key, value in locals_dict.items():
            if key.startswith('__'):
                continue

            safe_dict[key] = self._safe_copy(value)

        return safe_dict

    def _safe_copy(self, value: Any) -> Any:
        """Create a safe copy of a value for serialization."""
        if self._is_serializable(value):
            return value
        
        if isinstance(value, list):
            try:
                return [self._safe_copy(item) for item in value]
            except Exception:
                return f"<list with {len(value)} items>"
        
        if isinstance(value, dict):
            try:
                return {str(k): self._safe_copy(v) for k, v in list(value.items())[:10]}
            except Exception:
                return f"<dict with {len(value)} keys>"
        
        if isinstance(value, tuple):
            try:
                return tuple(self._safe_copy(item) for item in value)
            except Exception:
                return f"<tuple with {len(value)} items>"
        
        if isinstance(value, set):
            try:
                return list(self._safe_copy(item) for item in list(value)[:10])
            except Exception:
                return f"<set with {len(value)} items>"
        
        if isinstance(value, (int, float, str, bool, type(None))):
            return value
        
        return f"<{type(value).__name__}>"

    def _is_serializable(self, value: Any) -> bool:
        """Check if a value can be pickled."""
        if isinstance(value, (int, float, str, bool, list, dict, tuple, set, type(None))):
            return True
            
        if inspect.ismodule(value):
            return False
        if inspect.isfunction(value):
            return False
        if inspect.isclass(value):
            return False
        if isinstance(value, (threading.Lock, threading.RLock)):
            return False

        try:
            pickle.dumps(value)
            return True
        except (pickle.PickleError, TypeError, AttributeError):
            return False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()