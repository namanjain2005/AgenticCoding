# calculator/main.py

import sys
from pkg.calculator import Calculator
from pkg.render import format_json_output


def main():
    calculator = Calculator()
    if len(sys.argv) <= 1:
        print("Calculator App")
        print('Usage: python main.py "<expression>"')
        print('Example: python main.py "3 + 5"')
        return

    # Join the command‑line arguments to form the expression.
    # When the expression is passed quoted on the command line, the quotes become part of the first
    # and last tokens (e.g. "\"2 + 2\"").  Strip a single pair of surrounding quotes if present.
    expression = " ".join(sys.argv[1:]).strip()
    if (expression.startswith('"') and expression.endswith('"')) or (
            expression.startswith("'") and expression.endswith("'")):
        expression = expression[1:-1]

    try:
        result = calculator.evaluate(expression)
        if result is not None:
            to_print = format_json_output(expression, result)
            print(to_print)
        else:
            print("Error: Expression is empty or contains only whitespace.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
