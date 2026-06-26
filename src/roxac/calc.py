"""
Calculator core.
Provides full-precision arithmetic (no rounding) using Python's Decimal
with a configurable significant-digit precision.
"""

from decimal import Decimal, getcontext, InvalidOperation

from .constants import DECIMAL_PRECISION, VALID_OPERATORS
from .exceptions import InvalidExpression

# Set global decimal precision once at import time.
getcontext().prec = DECIMAL_PRECISION


def calculate(num1: str, operator: str, num2: str) -> str:
    """
    Perform a single arithmetic operation with full precision.

    Args:
        num1:     First operand as a string (integer or decimal).
        operator: One of +, -, *, /.
        num2:     Second operand as a string.

    Returns:
        The result as a clean string without unnecessary trailing zeros.

    Raises:
        InvalidExpression: For unsupported operators, non-numeric inputs,
                           or division by zero.
    """
    if operator not in VALID_OPERATORS:
        raise InvalidExpression(
            f"Invalid operator '{operator}'. Supported operators: + - * /"
        )

    try:
        a = Decimal(num1)
        b = Decimal(num2)
    except InvalidOperation:
        raise InvalidExpression(f"Invalid number(s): '{num1}', '{num2}'")

    if operator == "+":
        result = a + b
    elif operator == "-":
        result = a - b
    elif operator == "*":
        result = a * b
    elif operator == "/":
        if b == 0:
            raise InvalidExpression("Division by zero is undefined in this universe.")
        result = a / b

    return _format_decimal(result)


def _format_decimal(d: Decimal) -> str:
    """
    Format a Decimal result for clean terminal output.

    Uses fixed-point notation (never scientific notation) and strips
    trailing zeros/dots so '4.00' becomes '4' and '1.50' becomes '1.5'.
    """
    # Fixed-point notation avoids '1E+24' style output for large integers.
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s