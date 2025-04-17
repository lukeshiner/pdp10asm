from unittest import mock

import pytest

from pdp10asm.constants import Constants
from pdp10asm.exceptions import AssemblyError
from pdp10asm.expressions import ExpressionParser, Operations


@pytest.fixture
def assembler():
    return mock.Mock()


@pytest.mark.parametrize(
    "text,radix,expected",
    (
        ("10", 8, 8),
        ("10", 10, 10),
        ("101", 2, 5),
        ("FF", 16, 255),
    ),
)
def test_parse_number(text, radix, expected):
    assert ExpressionParser.value_to_int(text, radix=radix) == expected


def test_parse_expression_with_no_operators(assembler):
    get_symbol_value = assembler.symbol_table.get_symbol_value
    get_symbol_value.return_value = 25
    symbol = "FOO"
    assert ExpressionParser(symbol, assembler).value == get_symbol_value.return_value
    get_symbol_value.assert_called_once_with(symbol)


def test_addition_operation():
    assert Operations.addition_operation(10, 15) == 25


def test_subtraction_operation():
    assert Operations.subtraction_operation(50, 15) == 35


def test_multiply_operation():
    assert Operations.multiply_operation(50, 10) == 500


def test_divide_operation():
    assert Operations.divide_operation(7, 3) == 2


def test_and_operation():
    assert Operations.and_operation(5, 6) == 4


def test_or_operation():
    assert Operations.or_operation(5, 2) == 7


def test_calling_operation_by_name():
    assert ExpressionParser.operations[Constants.ADDITION_OPERATOR](10, 20) == 30


@pytest.mark.parametrize(
    "string,expected",
    (
        ("5", ["5"]),
        ("-5", ["-5"]),
        ("5+1", ["5", "+", "1"]),
        ("-5+1", ["-5", "+", "1"]),
        ("foo 5 + 12", ["foo 5", "+", "12"]),
        ("-5+-1", ["-5", "+", "-1"]),
        ("-5--1", ["-5", "-", "-1"]),
    ),
)
def test_expression_lexer(string, expected):
    assert ExpressionParser.expression_lexer(string) == expected


@mock.patch("pdp10asm.expressions.ExpressionParser.parse")
def test_as_literal(mock_parse):
    parser = ExpressionParser("", None)
    parser.validate_value = mock.Mock()
    assert parser.as_literal() == mock_parse.return_value
    parser.validate_value.assert_called_once_with(mock_parse.return_value)


@mock.patch("pdp10asm.expressions.ExpressionParser.parse")
def test_as_twos_complement(mock_parse):
    parser = ExpressionParser("", None)
    parser.validate_value = mock.Mock()
    parser.to_twos_complement = mock.Mock()
    assert parser.as_twos_complement() == parser.to_twos_complement.return_value
    parser.to_twos_complement.assert_called_once_with(mock_parse.return_value)
    parser.validate_value.assert_called_once_with(
        parser.to_twos_complement.return_value
    )


@pytest.mark.parametrize(
    "text,expected",
    (
        ("1", 1),
        ("1+1", 2),
        ("5-3", 2),
        (".-1", 4),
        ("FOO+1", 26),
        ("FOO-1", 24),
        ("FOO+FOO", 50),
        (".+FOO", 30),
        ("FOO+FOO+1", 51),
        ("FOO+FOO+1-FOO", 26),
        ("-6", -6),
        ("FOO-37", -6),
        ("-5+1", -4),
        ("-5+-1", -6),
        ("5&6", 4),
        ("5|2", 7),
        ("7/3", 2),
        ("4*2", 8),
        ("7+30/10*4+6", 25),
        (" 7 + 30 / 10 * 4 + 6 ", 25),
        ("5 - 7 ", -2),
    ),
)
def test_parse(text, expected, assembler):
    assembler.symbol_table.get_symbol_value.return_value = 25
    assembler.current_pass.program_counter = 5
    assert ExpressionParser(text, assembler).value == expected


def test_parse_with_no_operator():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser("text", mock.Mock())._parse_expression(["1", "2"])
    assert str(exc_info.value) == "Value operator mismatch."


@pytest.mark.parametrize(
    "value,expected",
    (
        (0, 0),
        (1, 1),
        (273405392, 273405392),
        (-6, 0b111111111111111111111111111111111010),
        (-54, 0b111111111111111111111111111111001010),
        (-273405392, 0b111111101111101101000010101000110000),
    ),
)
def test_to_twos_complement(value, expected):
    assert ExpressionParser.to_twos_complement(value) == expected


@pytest.mark.parametrize("value", (0, 1, 0o777777777777))
def test_validate_value_does_not_raise_for_valid_value(value):
    ExpressionParser.validate_value(value)


def test_validate_value_raises_if_value_negative():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_value(-1)
    assert str(exc_info.value) == "-1 is not a 36-bit number."


def test_validate_value_raises_if_value_too_large():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_value(0o1000000000000)
    assert str(exc_info.value) == "68719476736 is not a 36-bit number."
