# Rewind



Time-travel debugging for Python.



Record program execution once. Navigate through every line. Find bugs in seconds.





## Features



- Time travel navigation through execution history

- Side-by-side diff between any two frames

- Variable search across all recorded frames

- Terminal user interface with keyboard navigation

- Command line tools for analysis

- Zero code changes required





## Installation



&#x20;   pip install rewind-debugger



Requires Python 3.9 or higher.





## Quick Start



Record your program:



&#x20;   from rewind import Recorder

&#x20;   

&#x20;   recorder = Recorder("trace.db")

&#x20;   recorder.start()

&#x20;   

&#x20;   result = buggy\_function()

&#x20;   

&#x20;   recorder.stop()



Debug with time travel:



&#x20;   rewind replay trace.db



Use left/right arrow keys to move through execution frames.





## Documentation



Full documentation is available in docs/user\_guide.md



Key topics:

- Recording programs via API or command line

- TUI navigation shortcuts

- Diff and search commands

- Python API reference

- Troubleshooting common issues





## Command Line Reference



&#x20;   rewind record <script> -o <trace>

&#x20;       Record execution of a Python script.



&#x20;   rewind replay <trace>

&#x20;       Open interactive debugger.



&#x20;   rewind diff <trace> <frame\_a> <frame\_b>

&#x20;       Compare two frames.



&#x20;   rewind search <trace> <variable\_name>

&#x20;       Find variable across all frames.



&#x20;   rewind info

&#x20;       Display version information.





## Examples



Example 1: Record and debug a buggy calculator



&#x20;   # demo.py

&#x20;   from rewind import Recorder

&#x20;   

&#x20;   def buggy\_calculator(prices, discount):

&#x20;       total = 0

&#x20;       for price in prices:

&#x20;           total += price \* discount  # Bug: should be price \* (1 - discount)

&#x20;       return total

&#x20;   

&#x20;   recorder = Recorder("bug.trace")

&#x20;   recorder.start()

&#x20;   

&#x20;   result = buggy\_calculator(\[100, 200, 300], 0.1)

&#x20;   print(f"Result: {result}")

&#x20;   

&#x20;   recorder.stop()



Run debugger:



&#x20;   rewind replay bug.trace



Navigate to frame 3. See that `discount` is 0.1 but should be 0.9 for 10% off.



Example 2: Find where a variable changes



&#x20;   rewind search trace.db counter



Output shows every frame where `counter` appears with its value.



Example 3: Compare state before and after function call



&#x20;   rewind diff trace.db 10 15



Output shows exactly which variables changed between line 10 and line 15.





## How It Works



Rewind uses Python's sys.settrace() to capture execution state at each line:



1\. Recorder hooks into the interpreter

2\. At each line, local variables are serialized and compressed

3\. Snapshots are stored in SQLite

4\. Player loads snapshots and enables navigation

5\. TUI provides keyboard-driven exploration



Recording overhead is approximately 2-5x for pure Python code. Trace size averages 1KB per 100 lines of execution.





## Limitations



- Only records main thread (child threads not captured)

- Async function support is limited

- Non-serializable objects become type placeholders

- Not suitable for production monitoring

- Long-running scripts produce large trace files





## Contributing



Contributions are welcome.



Setup development environment:



&#x20;   git clone https://github.com/rewind/rewind.git

&#x20;   cd rewind

&#x20;   pip install -e .\[dev]



Run tests:



&#x20;   pytest tests/ -v



Run linters:



&#x20;   black rewind/

&#x20;   isort rewind/

&#x20;   mypy rewind/





## License



MIT License





## Links



- Source: https://github.com/rewind/rewind

- Issues: https://github.com/rewind/rewind/issues

- Documentation: docs/user\_guide.md

