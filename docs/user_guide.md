Rewind User Guide



Table of Contents



1\. Installation

2\. Quick Start

3\. Recording

4\. Replaying

5\. Command Line Interface

6\. Python API Reference

7\. Troubleshooting

8\. Limitations





1\. Installation



Install Rewind via pip:



&#x20;   pip install rewind-debugger



Verify installation:



&#x20;   rewind info





2\. Quick Start



Step 1: Record a program



&#x20;   from rewind import Recorder

&#x20;   

&#x20;   recorder = Recorder("trace.db")

&#x20;   recorder.start()

&#x20;   

&#x20;   # Your code here

&#x20;   x = 10

&#x20;   y = 20

&#x20;   result = x + y

&#x20;   

&#x20;   recorder.stop()



Step 2: Debug with time travel



&#x20;   rewind replay trace.db



Use arrow keys to navigate through execution frames.





3\. Recording



3.1 Python API



Basic recording:



&#x20;   from rewind import Recorder

&#x20;   

&#x20;   recorder = Recorder("path/to/trace.db")

&#x20;   recorder.start()

&#x20;   

&#x20;   # Your program logic

&#x20;   data = process\_input()

&#x20;   

&#x20;   recorder.stop()

&#x20;   recorder.save()



Context manager pattern:



&#x20;   from rewind import Recorder

&#x20;   

&#x20;   with Recorder("trace.db") as recorder:

&#x20;       result = buggy\_function()

&#x20;       # Recorder automatically stops when exiting block



3.2 Command Line Recording



Record any Python script:



&#x20;   rewind record my\_script.py -o trace.db



Record with arguments:



&#x20;   rewind record my\_script.py -o trace.db --args "--verbose --config config.json"



3.3 What Gets Recorded



For each line of execution, Rewind captures:



\- Line number

\- Filename

\- Function name

\- Local variables (serializable ones)

\- Timestamp



Non-serializable objects (modules, file handles, locks) are replaced with type names like `<module object>` or `<file object>`.





4\. Replaying



4.1 Terminal User Interface (TUI)



Launch the debugger:



&#x20;   rewind replay trace.db



Keyboard shortcuts:



&#x20;   Left Arrow / Right Arrow     Navigate between frames

&#x20;   g                            Go to specific frame number

&#x20;   d                            Show diff with previous frame

&#x20;   s                            Search for variable across all frames

&#x20;   h                            Display help screen

&#x20;   q                            Quit debugger



The TUI displays:



\- Current frame number and total frames

\- File location (filename:line\_number in function\_name)

\- Local variables with their values and types

\- Help bar with available commands



4.2 Navigating Large Traces



To jump directly to a frame:



&#x20;   rewind replay trace.db --frame 500



To search before launching TUI:



&#x20;   rewind search trace.db variable\_name





5\. Command Line Interface



5.1 Record Command



&#x20;   rewind record <script> \[OPTIONS]



Options:

&#x20;   -o, --output TEXT     Output trace file path (default: trace.db)

&#x20;   -a, --args TEXT       Arguments to pass to the script



Example:

&#x20;   rewind record app.py -o production\_bug.trace --args "--env prod"



5.2 Replay Command



&#x20;   rewind replay <trace> \[OPTIONS]



Options:

&#x20;   -f, --frame INTEGER   Start at specific frame number



Example:

&#x20;   rewind replay bug.trace --frame 42



5.3 Diff Command



&#x20;   rewind diff <trace> <frame\_a> <frame\_b>



Output shows:

&#x20;   - Added variables (present in B but not A)

&#x20;   - Removed variables (present in A but not B)

&#x20;   - Modified variables with before/after values



Example:

&#x20;   rewind diff trace.db 10 15



Sample output:



&#x20;   Diff: Frame 10 -> Frame 15



&#x20;   Added: result, temp\_value

&#x20;   Removed: counter

&#x20;   Modified:

&#x20;       total: 100 -> 150

&#x20;       status: pending -> completed



5.4 Search Command



&#x20;   rewind search <trace> <variable\_name>



Searches for a variable across all recorded frames and displays where it appears.



Example:

&#x20;   rewind search trace.db user\_id



Sample output:



&#x20;   Searching for 'user\_id' in trace.db



&#x20;   Found in 3 frame(s):



&#x20;   Frame    5: 42

&#x20;   Frame   12: 42

&#x20;   Frame   89: 100



5.5 Info Command



&#x20;   rewind info



Displays version and helpful links.





6\. Python API Reference



6.1 Recorder Class



Recorder(trace\_path: str = "trace.db")



Methods:



&#x20;   start() -> None

&#x20;       Begin recording execution. Raises RecordingError if already recording.



&#x20;   stop() -> None

&#x20;       Stop recording execution.



&#x20;   save() -> None

&#x20;       Save trace to disk.



Context manager support:

&#x20;   with Recorder("trace.db") as recorder:

&#x20;       # code here



6.2 Player Class



Player(trace\_path: str)



Methods:



&#x20;   get\_frame(index: int) -> FrameInfo

&#x20;       Retrieve frame by index. Raises FrameNotFoundError if index invalid.



&#x20;   goto\_frame(index: int) -> FrameInfo

&#x20;       Alias for get\_frame.



&#x20;   diff\_frames(index\_a: int, index\_b: int) -> Dict

&#x20;       Compare two frames. Returns dict with keys:

&#x20;       - added: list of variable names

&#x20;       - removed: list of variable names

&#x20;       - modified: dict with before/after values

&#x20;       - unchanged: list of variable names



&#x20;   search\_variable(var\_name: str) -> List\[Tuple\[int, Any]]

&#x20;       Find all frames containing variable. Returns list of (frame\_index, value).



&#x20;   frame\_count -> int (property)

&#x20;       Total number of recorded frames.



6.3 FrameInfo Dataclass



Attributes:



&#x20;   index: int

&#x20;       Frame number in sequence.



&#x20;   line\_no: int

&#x20;       Line number in source file.



&#x20;   filename: str

&#x20;       Absolute or relative path to source file.



&#x20;   function\_name: str

&#x20;       Name of containing function.



&#x20;   timestamp: float

&#x20;       Unix timestamp when frame was recorded.



&#x20;   locals: Dict\[str, Any]

&#x20;       Local variables at this frame.



6.4 Exceptions



&#x20;   RewindError

&#x20;       Base exception for all Rewind errors.



&#x20;   RecordingError

&#x20;       Raised when recording operations fail.



&#x20;   ReplayError

&#x20;       Raised when replay operations fail.



&#x20;   TraceCorruptedError

&#x20;       Raised when trace file is corrupted or schema mismatched.



&#x20;   FrameNotFoundError

&#x20;       Raised when requested frame index is out of range.





7\. Troubleshooting



7.1 Recording fails with "Failed to create trace storage"



Ensure you have write permissions in the output directory. Check disk space.



7.2 Trace file is very large



Long-running scripts generate large trace files. Consider:

&#x20;   - Recording only the problematic section, not the entire program

&#x20;   - Using the context manager to limit recording scope



7.3 Variables show as <object> instead of values



Non-serializable objects (modules, file objects, network connections, locks) cannot be pickled. Rewind replaces them with a placeholder showing the type name.



To inspect such objects, add logging before the problematic line.



7.4 Replay is slow with large traces



SQLite performs well up to tens of thousands of frames. For larger traces, use command-line diff/search instead of TUI navigation.



7.5 Recorder doesn't capture variables inside comprehensions



List/dict/set comprehensions and generator expressions execute in a separate frame. Variables defined inside are captured normally.



7.6 Multi-threaded programs produce inconsistent traces



Current version records only the main thread. Support for multi-threading is planned for future releases.



7.7 Recorder captures too many frames from internal code



Rewind automatically skips frames from its own modules and common internal functions. To add custom exclusions, extend the \_should\_skip\_frame method in Recorder class.





8\. Limitations



Python Version

&#x20;   Requires Python 3.9 or higher.



Performance

&#x20;   Recording adds 2-5x overhead. Not suitable for production monitoring.



Threading

&#x20;   Only the main thread is recorded. Child threads are not captured.



Async/Await

&#x20;   Limited support for async functions. Frames inside async calls may be incomplete.



External I/O

&#x20;   Network requests, file writes, and database operations are recorded as they occur but cannot be undone during replay.



Memory Usage

&#x20;   Trace files can become large for long-running scripts. Each frame stores a compressed snapshot of local variables.



Serialization

&#x20;   Objects that cannot be pickled are replaced with type placeholders. This includes modules, file objects, sockets, and database connections.



Production Use

&#x20;   Rewind is designed for debugging, not production monitoring. Do not enable recording in production environments.



Platform Support

&#x20;   Works on any platform where Python runs (Linux, macOS, Windows). No platform-specific dependencies.

