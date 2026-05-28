"""Example buggy script for testing."""

def calculate_total(prices, tax_rate):
    total = 0
    for price in prices:
        total += price
    return total * (1 + tax_rate)


def main():
    prices = [100, 200, 300]
    tax_rate = 0.1

    result = calculate_total(prices, tax_rate)
    print(f"Total with tax: {result}")


if __name__ == '__main__':
    main()