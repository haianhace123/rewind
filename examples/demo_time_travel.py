"""Advanced demonstration of time-travel debugging."""

import sys
sys.path.insert(0, '.')

from rewind import Recorder


def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def buggy_factorial(n):
    result = 1
    for i in range(n):
        result *= i
    return result


if __name__ == "__main__":
    print("🕰️ Time-Travel Debugging Demo\n")

    recorder = Recorder("advanced.trace")
    recorder.start()

    print("Computing fibonacci(5)...")
    fib_result = fibonacci(5)
    print(f"fib(5) = {fib_result}")

    print("\nComputing buggy factorial(5)...")
    fact_result = buggy_factorial(5)
    print(f"factorial(5) = {fact_result} (should be 120)")

    recorder.stop()

    print("\n✅ Trace saved to advanced.trace")
    print("\nDebug with: rewind replay advanced.trace")
    print("Commands:")
    print("  → : next frame")
    print("  ← : previous frame")
    print("  d : diff with previous frame")
    print("  s : search for variable 'result'")