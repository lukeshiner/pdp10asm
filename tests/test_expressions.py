from unittest import mock

import pytest

from pdp10asm.constants import Constants
from pdp10asm.exceptions import AssemblyError
from pdp10asm.expressions import ExpressionParser, Operations


@pytest.fixture
def assembler():
    return mock.Mock(radix=8)


@pytest.fixture
def parser(assembler):
    return ExpressionParser("text", assembler)


def test_expression_parser_has_text(parser):
    assert parser.text == "text"


def test_expression_parser_has_assembler(parser, assembler):
    assert parser.assembler == assembler


def test_expression_parser_has_radix(parser):
    assert parser.radix is None


def test_expression_parser_takes_radix(assembler):
    assert ExpressionParser("text", assembler, radix=10).radix == 10


@pytest.mark.parametrize(
    "text,expected",
    (
        ("10", 8),
        ("^O10", 8),
        ("^D10", 10),
        ("^D 10", 10),
        ("^B101", 5),
        ("5K", 5000),
        ("5M", 5000000),
        ("5 G", 5000000000),
        ("^O10K", 8000),
        ("^D10M", 10000000),
        ("^D 10 G", 10000000000),
        ("^B101 K", 5000),
    ),
)
def test_parse_number(text, expected, parser):
    assert parser.value_to_int(text) == expected


@pytest.mark.parametrize(
    "text,parser_radix,assembler_radix,value,radix",
    (
        ("10", None, 8, "10", 8),
        ("^O10", None, 8, "10", 8),
        ("^D10", None, 8, "10", 10),
        ("^D 10", None, 8, "10", 10),
        ("^B101", None, 8, "101", 2),
        ("10", 8, 8, "10", 8),
        ("^O10", 8, 8, "10", 8),
        ("^D10", 8, 8, "10", 10),
        ("^D 10", 8, 8, "10", 10),
        ("^B101", 8, 8, "101", 2),
        ("10", 10, 8, "10", 10),
        ("^O10", 10, 8, "10", 8),
        ("^D10", 10, 8, "10", 10),
        ("^D 10", 10, 8, "10", 10),
        ("^B101", 10, 8, "101", 2),
        ("10", None, 5, "10", 5),
        ("^O10", None, 5, "10", 8),
        ("^D10", None, 5, "10", 10),
        ("^D 10", None, 5, "10", 10),
        ("^B101", None, 5, "101", 2),
        ("10", 8, 5, "10", 8),
        ("^O10", 8, 5, "10", 8),
        ("^D10", 8, 5, "10", 10),
        ("^D 10", 8, 5, "10", 10),
        ("^B101", 8, 5, "101", 2),
        ("10", 10, 5, "10", 10),
        ("^O10", 10, 5, "10", 8),
        ("^D10", 10, 5, "10", 10),
        ("^D 10", 10, 5, "10", 10),
        ("^B101", 10, 5, "101", 2),
    ),
)
def test_handle_radix(text, parser_radix, assembler_radix, value, radix, parser):
    parser.assembler.radix = assembler_radix
    parser.radix = parser_radix
    assert parser.handle_radix(text) == (value, radix)


@pytest.mark.parametrize(
    "text,value,magnitude",
    (
        ("10", "10", 1),
        ("10K", "10", 1000),
        ("10M", "10", 1000000),
        ("10G", "10", 1000000000),
        ("5", "5", 1),
        ("5 K", "5", 1000),
        ("5 M", "5", 1000000),
        ("5 G", "5", 1000000000),
    ),
)
def test_handle_magnitude(text, value, magnitude, parser):
    assert parser.handle_magnitude(text) == (value, magnitude)


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
    "text,token,string",
    (
        ("5", "5", None),
        ("1+2", "1", "+2"),
        ("+2-", "+", "2-"),
        ("FOO 5 + 7", "FOO 5", "+ 7"),
        ("+ < 3+5>", "+", "< 3+5>"),
    ),
)
def test_get_token(text, token, string):
    returned_token, returned_string = ExpressionParser.get_token(text)
    assert returned_token == token
    assert returned_string == string


@pytest.mark.parametrize(
    "string,expected",
    (
        ("5", ["5"]),
        ("-5", ["-", "5"]),
        ("5+1", ["5", "+", "1"]),
        ("-5+1", ["-", "5", "+", "1"]),
        ("foo 5 + 12", ["foo 5", "+", "12"]),
        ("-5+-1", ["-", "5", "+", "-", "1"]),
        ("-5--1", ["-", "5", "-", "-", "1"]),
        ("5+<3-2>", (["5", "+", ["3", "-", "2"]])),
        ("6+<5+<7-5>*4>", ["6", "+", ["5", "+", ["7", "-", "5"], "*", "4"]]),
        ("5 + <3 * 2>", ["5", "+", ["3", "*", "2"]]),
        ("<5 + 3> * 2", [["5", "+", "3"], "*", "2"]),
        ("5 + <3 + <6 + 9>>", ["5", "+", ["3", "+", ["6", "+", "9"]]]),
    ),
)
def test_expression_lexer(string, expected):
    assert ExpressionParser.expression_lexer(string) == expected


@mock.patch("pdp10asm.expressions.ExpressionParser.parse")
def test_as_literal(mock_parse):
    parser = ExpressionParser("", None)
    parser.validate_word = mock.Mock()
    assert parser.as_literal() == mock_parse.return_value
    parser.validate_word.assert_called_once_with(mock_parse.return_value)


@mock.patch("pdp10asm.expressions.ExpressionParser.parse")
def test_as_twos_complement(mock_parse):
    parser = ExpressionParser("", None)
    parser.validate_word = mock.Mock()
    parser.to_twos_complement = mock.Mock()
    assert parser.as_twos_complement() == parser.to_twos_complement.return_value
    parser.to_twos_complement.assert_called_once_with(mock_parse.return_value)
    parser.validate_word.assert_called_once_with(parser.to_twos_complement.return_value)


@pytest.mark.parametrize(
    "value,negative,expected",
    (
        (1, False, 1),
        (2, False, 2),
        (-1, True, 1),
        (-1, False, 262143),
        (1, True, 262143),
    ),
)
@mock.patch("pdp10asm.expressions.ExpressionParser.parse")
def test_as_half_word(mock_parse, value, negative, expected):
    parser = ExpressionParser("", None)
    parser.value = value
    parser.validate_half_word = mock.Mock()
    assert parser.as_half_word(negative=negative) == expected
    parser.validate_half_word.assert_called_once_with(expected)


@pytest.mark.parametrize(
    "text,expected",
    (
        ("1", 1),
        ("-1", -1),
        ("-56", -0o56),
        ("56", 0o56),
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
        ("5 + <3 * 2>", 11),
        ("<5 + 3> * 2", 16),
        ("5 * <3 * <4+1> -1>", 70),
    ),
)
def test_parse(text, expected, assembler):
    assembler.symbol_table.get_symbol_value.return_value = 25
    assembler.current_pass.program_counter = 5
    assert ExpressionParser(text, assembler).value == expected


def test_parse_with_no_operator():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser("text", mock.Mock())._parse_expression(["1", "2"])
    assert str(exc_info.value) == "Value operator mismatch ['1', '2']."


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
def test_validate_word_does_not_raise_for_valid_value(value):
    ExpressionParser.validate_word(value)


def test_validate_word_raises_if_value_negative():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_word(-1)
    assert str(exc_info.value) == "-1 is not a 36-bit number."


def test_validate_word_raises_if_value_too_large():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_word(0o1000000000000)
    assert str(exc_info.value) == "68719476736 is not a 36-bit number."


@pytest.mark.parametrize("value", (0, 1, 0o777777))
def test_validate_half_word_does_not_raise_for_valid_value(value):
    ExpressionParser.validate_half_word(value)


def test_validate_half_word_raises_if_value_negative():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_half_word(-1)
    assert str(exc_info.value) == "-1 is not an 18-bit number."


def test_validate_half_word_raises_if_value_too_large():
    with pytest.raises(AssemblyError) as exc_info:
        ExpressionParser.validate_half_word(0o1000000)
    assert str(exc_info.value) == "262144 is not an 18-bit number."
