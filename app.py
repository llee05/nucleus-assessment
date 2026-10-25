"""Calculation logic for the calculator's form submissions."""

import re
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext


def calculate(first_number: str, operation: str, second_number: str) -> str:
    """Return a formatted result, or raise ValueError for invalid input.

    Operands are decimal strings, up to 32 characters after trimming.
    Operations are add, subtract, multiply, and divide. Arithmetic uses
    28 significant digits with round-half-even; repeating decimals round.
    """
    if not isinstance(first_number, str) or not isinstance(second_number, str):
        raise ValueError("Enter valid decimal numbers.")

    first_number = first_number.strip()
    second_number = second_number.strip()
    if not first_number or not second_number:
        raise ValueError("Enter both numbers.")

    for number in (first_number, second_number):
        if len(number) > 32:
            raise ValueError("Use at most 32 characters per number.")
        if not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", number):
            raise ValueError("Enter valid decimal numbers.")

    if operation not in ("add", "subtract", "multiply", "divide"):
        raise ValueError("Choose a supported operation.")

    # Parse strings directly: converting through float would lose precision.
    first = Decimal(first_number)
    second = Decimal(second_number)
    if operation == "divide" and second == 0:
        raise ValueError("Cannot divide by zero.")

    # A local context keeps arithmetic independent of other application code.
    with localcontext(Context(prec=28, rounding=ROUND_HALF_EVEN)):
        if operation == "add":
            result = first + second
        elif operation == "subtract":
            result = first - second
        elif operation == "multiply":
            result = first * second
        else:
            result = first / second

    if result == 0:
        return "0"

    display = format(result, "f")
    # Strip fractional zeros only, so an integer such as 50 remains intact.
    return display.rstrip("0").rstrip(".") if "." in display else display
