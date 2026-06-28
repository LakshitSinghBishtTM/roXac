"Tests for calc.py."

import pytest
from roxac.calc import calculate
from roxac.exceptions import InvalidExpression


class TestBasicOperations:
    def test_addition(self):
        assert calculate("1", "+", "2") == "3"

    def test_subtraction(self):
        assert calculate("10", "-", "3") == "7"

    def test_multiplication(self):
        assert calculate("3", "*", "4") == "12"

    def test_division_exact(self):
        assert calculate("10", "/", "2") == "5"


class TestPrecision:
    def test_no_float_rounding(self):
        # Classic float trap: 0.1 + 0.2 == 0.3 exactly with Decimal
        assert calculate("0.1", "+", "0.2") == "0.3"

    def test_division_repeating_decimal(self):
        result = calculate("1", "/", "3")
        # Should produce many digits, not just 0.33
        assert result.startswith("0.")
        assert len(result) > 20

    def test_large_integers(self):
        assert calculate("999999999999999999", "+", "1") == "1000000000000000000"

    def test_no_scientific_notation(self):
        result = calculate("1000000", "*", "1000000")
        assert "E" not in result and "e" not in result
        assert result == "1000000000000"

    def test_strips_trailing_zeros(self):
        assert calculate("1.50", "+", "0.50") == "2"

    def test_strips_trailing_decimal_point(self):
        assert calculate("3.0", "*", "2.0") == "6"

    def test_check_negative_zero(self):
        assert calculate("-3", "*", "0") == "0"


class TestEdgeCases:
    def test_negative_numbers(self):
        assert calculate("-5", "+", "3") == "-2"

    def test_negative_result(self):
        assert calculate("3", "-", "10") == "-7"

    def test_division_by_zero(self):
        with pytest.raises(InvalidExpression, match="Undefined!"):
            calculate("5", "/", "0")

    def test_invalid_operator(self):
        with pytest.raises(InvalidExpression):
            calculate("1", "%", "2")

    def test_invalid_number_first(self):
        with pytest.raises(InvalidExpression):
            calculate("abc", "+", "2")

    def test_invalid_number_second(self):
        with pytest.raises(InvalidExpression):
            calculate("1", "+", "xyz")

    def test_x_operator_not_accepted(self):
        # 'x' is a CLI alias normalised before reaching calc.py
        with pytest.raises(InvalidExpression):
            calculate("3", "x", "4")