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
        assert calculate("0.1", "+", "0.2") == "0.3"

    def test_division_repeating_decimal(self):
        result = calculate("1", "/", "3")
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
        with pytest.raises(InvalidExpression):
            calculate("3", "x", "4")


class TestZeroResultSign:
    def test_subtracting_equal_numbers(self):
        assert calculate("5", "-", "5") == "0"

    def test_adding_opposite_numbers(self):
        assert calculate("-5", "+", "5") == "0"

    def test_multiplying_negative_by_zero(self):
        assert calculate("-3", "*", "0") == "0"

    def test_multiplying_zero_by_negative(self):
        assert calculate("0", "*", "-7") == "0"

    def test_subtracting_zero_decimals(self):
        assert calculate("0", "-", "0.0") == "0"

    def test_negative_zero_result_is_clean_zero(self):
        assert calculate("0", "*", "-1") == "0"


class TestNonFiniteInputs:
    NON_FINITE = ["inf", "-inf", "Infinity", "-Infinity", "nan", "NaN"]
    OPS = ["+", "-", "*", "/"]

    @pytest.mark.parametrize("op", OPS)
    @pytest.mark.parametrize("bad", NON_FINITE)
    def test_non_finite_first_operand_rejected(self, bad, op):
        with pytest.raises(InvalidExpression):
            calculate(bad, op, "5")

    @pytest.mark.parametrize("op", OPS)
    @pytest.mark.parametrize("bad", NON_FINITE)
    def test_non_finite_second_operand_rejected(self, bad, op):
        with pytest.raises(InvalidExpression):
            calculate("5", op, bad)

    def test_inf_minus_inf_does_not_crash(self):
        with pytest.raises(InvalidExpression):
            calculate("inf", "-", "inf")

    def test_inf_times_zero_does_not_crash(self):
        with pytest.raises(InvalidExpression):
            calculate("inf", "*", "0")

    def test_finite_divided_by_inf_does_not_blow_up_output(self):
        with pytest.raises(InvalidExpression):
            calculate("5", "/", "inf")


class TestUnderscoreGroupingRejected:
    def test_underscore_in_first_operand_rejected(self):
        with pytest.raises(InvalidExpression):
            calculate("5_000", "+", "5")

    def test_underscore_in_second_operand_rejected(self):
        with pytest.raises(InvalidExpression):
            calculate("5", "+", "5_000")

    def test_underscore_in_decimal_rejected(self):
        with pytest.raises(InvalidExpression):
            calculate("1_0.5", "+", "1")
