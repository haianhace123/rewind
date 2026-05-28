"""Simple demonstration of Rewind recording."""

import sys
sys.path.insert(0, '.')

from rewind import Recorder


def buggy_calculator(prices, discount):
    result = []
    for price in prices:
        discounted = price * discount
        result.append(discounted)
    return sum(result)


if __name__ == "__main__":
    print("🎬 Recording demo...")

    recorder = Recorder("demo.trace")
    recorder.start()

    prices = [100, 200, 300]
    discount = 0.1

    wrong_result = buggy_calculator(prices, discount)
    expected = 540

    print(f"Buggy result: {wrong_result}")
    print(f"Expected: {expected}")

    recorder.stop()

    print("\n✅ Trace saved to demo.trace")
    print("\nNow run: rewind replay demo.trace")
    print("Use ← → to navigate through frames and inspect variables")