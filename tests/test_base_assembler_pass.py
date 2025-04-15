import types
from unittest import mock

import pytest

from pdp10asm.constants import Constants
from pdp10asm.exceptions import AssemblyError
from pdp10asm.passes import BaseAssemblerPass
from pdp10asm.symbol_table import SymbolTable


@pytest.fixture
def mock_assembler():
    return mock.Mock()


@pytest.fixture
def base_pass(mock_assembler):
    _base_pass = BaseAssemblerPass(assembler=mock_assembler)
    _base_pass.symbol_table = SymbolTable()
    return _base_pass


@pytest.fixture
def symbol():
    return "FOO"


@pytest.fixture
def mock_parse_number(base_pass):
    base_pass.parse_number = mock.Mock()
    return base_pass.parse_number


@pytest.fixture
def mock_symbol_value(base_pass):
    base_pass.symbol_value = mock.Mock()
    return base_pass.symbol_value


@pytest.fixture
def mock_symbol_or_value(base_pass):
    base_pass.symbol_or_value = mock.Mock(return_value=127)
    return base_pass.symbol_or_value


@pytest.fixture
def mock_pseudo_operators(base_pass):
    base_pass.pseudo_operators = mock.Mock()
    return base_pass.pseudo_operators


def test_base_assmbler_pass_has_assembler(base_pass, mock_assembler):
    assert base_pass.assembler == mock_assembler


def test_base_assembler_pass_has_symbol_table(mock_assembler):
    base_pass = BaseAssemblerPass(assembler=mock_assembler)
    assert base_pass.symbol_table == mock_assembler.symbol_table


def test_base_assembler_pass_has_pseudo_operators(mock_assembler, base_pass):
    assert base_pass.pseudo_operators == mock_assembler.pseudo_operators


def test_base_assembler_pass_has_program_counter(base_pass):
    assert base_pass.program_counter == 0


def test_base_assembler_pass_has_source_line_number(base_pass):
    assert base_pass.source_line_number == 0


def test_base_assembler_pass_has_done_property(base_pass):
    assert base_pass.done is False


def test_base_assembler_pass_has_operations_property(base_pass):
    for key, value in base_pass.operations.items():
        assert isinstance(key, str)
        assert isinstance(value, types.FunctionType)


def test_process_line_raises_not_implemented(base_pass):
    with pytest.raises(NotImplementedError):
        base_pass.process_line([])


def test_run_method(base_pass):
    base_pass.process_line = mock.Mock()
    base_pass.assembler.source_lines = [mock.Mock(is_empty=False)] * 3
    base_pass.run()
    base_pass.process_line.assert_has_calls(
        (mock.call(source_line) for source_line in base_pass.assembler.source_lines),
        any_order=False,
    )


def test_run_method_skips_empty_instruction(base_pass):
    base_pass.process_line = mock.Mock()
    base_pass.assembler.source_lines = [
        mock.Mock(is_empty=False),
        mock.Mock(is_empty=True),
        mock.Mock(is_empty=False),
    ]
    base_pass.run()
    base_pass.process_line.assert_has_calls(
        (
            mock.call(base_pass.assembler.source_lines[0]),
            mock.call(base_pass.assembler.source_lines[2]),
        ),
        any_order=False,
    )


def test_run_method_stops_when_done_is_true(base_pass):
    base_pass.done = True
    base_pass.process_line = mock.Mock()
    base_pass.assembler.source_lines = [mock.Mock(is_empty=False)] * 3
    base_pass.run()
    base_pass.process_line.assert_not_called()


def test_run_method_does_not_increment_program_counter_when_source_line_is_not_assemblable(
    base_pass,
):
    base_pass.program_counter = 5
    base_pass.process_line = mock.Mock()
    base_pass.assembler.source_lines = [mock.Mock(is_empty=False, is_assemblable=False)]
    base_pass.run()
    base_pass.process_line.assert_called_once_with(base_pass.assembler.source_lines[0])
    assert base_pass.program_counter == 5


def test_run_method_increments_program_counter_when_source_line_is_assemblable(
    base_pass,
):
    base_pass.program_counter = 5
    base_pass.process_line = mock.Mock()
    base_pass.assembler.source_lines = [mock.Mock(is_empty=False, is_assemblable=True)]
    base_pass.run()
    base_pass.process_line.assert_called_once_with(base_pass.assembler.source_lines[0])
    assert base_pass.program_counter == 6


def test_handle_pseudo_operator_method(
    base_pass, mock_pseudo_operators, mock_parse_number
):
    source_line = mock.Mock(operator="INST", arguments="500 250")
    base_pass.handle_pseudo_operator(source_line)
    mock_parse_number.assert_has_calls(
        (
            mock.call("500"),
            mock.call("250"),
        ),
        any_order=False,
    )
    mock_pseudo_operators.process_instruction.assert_called_once_with(
        instruction_word="INST",
        values=[
            mock_parse_number.return_value,
            mock_parse_number.return_value,
        ],
    )


def test_symbol_value(base_pass, symbol):
    base_pass.symbol_table.add_user_symbol(symbol, 10, 10)
    assert base_pass.symbol_value(symbol) == 10


@mock.patch("pdp10asm.passes.SourceLine.is_symbol")
def test_symbol_or_value_with_symbol(
    mock_is_symbol, mock_parse_number, mock_symbol_value, symbol, base_pass
):
    mock_is_symbol.return_value = True
    return_value = base_pass.symbol_or_value(symbol)
    assert return_value == mock_symbol_value.return_value
    mock_is_symbol.assert_called_once_with(symbol)
    mock_symbol_value.assert_called_once_with(symbol)
    mock_parse_number.assert_not_called()


@mock.patch("pdp10asm.passes.SourceLine.is_symbol")
def test_symbol_or_value_with_value(
    mock_is_symbol, base_pass, mock_parse_number, mock_symbol_value, symbol
):
    mock_is_symbol.return_value = False
    return_value = base_pass.symbol_or_value(symbol)
    assert return_value == mock_parse_number.return_value
    mock_is_symbol.assert_called_once_with(symbol)
    mock_symbol_value.assert_not_called()
    mock_parse_number.assert_called_once_with(symbol)


@mock.patch("pdp10asm.passes.SourceLine.is_symbol")
def test_symbol_or_value_with_program_counter_symbol(
    mock_is_symbol, base_pass, mock_parse_number, mock_symbol_value, symbol
):
    return_value = base_pass.symbol_or_value(Constants.PROGRAM_COUNTER_OPERAND)
    assert return_value == base_pass.program_counter
    mock_is_symbol.assert_not_called()
    mock_symbol_value.assert_not_called()
    mock_parse_number.assert_not_called()


@pytest.mark.parametrize(
    "text,radix,expected",
    (
        ("10", 8, 8),
        ("10", 10, 10),
        ("101", 2, 5),
        ("FF", 16, 255),
    ),
)
def test_parse_number(text, radix, expected, base_pass):
    assert base_pass.parse_number(text, radix=radix) == expected


def test_parse_expression_with_no_operators(base_pass, mock_symbol_or_value, symbol):
    assert base_pass.parse_expression(symbol) == mock_symbol_or_value.return_value
    mock_symbol_or_value.assert_called_once_with(symbol)


def test_addition_operation(base_pass):
    assert base_pass.addition_operation(10, 15) == 25


def test_subtraction_operation(base_pass):
    assert base_pass.subtraction_operation(50, 15) == 35


def test_multiply_operation(base_pass):
    assert base_pass.multiply_operation(50, 10) == 500


def test_divide_operation(base_pass):
    assert base_pass.divide_operation(7, 3) == 2


def test_and_operation(base_pass):
    assert base_pass.and_operation(5, 6) == 4


def test_or_operation(base_pass):
    assert base_pass.or_operation(5, 2) == 7


def test_calling_operation_by_name(base_pass):
    assert base_pass.operations[Constants.ADDITION_OPERATOR](10, 20) == 30


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
        ("-6", 68719476730),
        ("FOO-37", 68719476730),
        ("-5+1", 68719476732),
        ("-5+-1", 68719476730),
        ("5&6", 4),
        ("5|2", 7),
        ("7/3", 2),
        ("4*2", 8),
    ),
)
def test_parse_expression(text, expected, base_pass):
    base_pass.symbol_table.add_user_symbol("FOO", 25, 1)
    base_pass.program_counter = 5
    assert base_pass.parse_expression(text) == expected


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
def test_int_to_twos_complement(value, expected, base_pass):
    assert base_pass.int_to_twos_complement(value) == expected


@pytest.mark.parametrize("value", (0, 1, 0o777777777777))
def test_validate_value_does_not_raise_for_valid_value(value, base_pass):
    base_pass.validate_value(value)


def test_validate_value_raises_if_value_negative(base_pass):
    with pytest.raises(AssemblyError) as exc_info:
        base_pass.validate_value(-1)
    assert str(exc_info.value) == "-1 is not a 36-bit number."


def test_validate_value_raises_if_value_too_large(base_pass):
    with pytest.raises(AssemblyError) as exc_info:
        base_pass.validate_value(0o1000000000000)
    assert str(exc_info.value) == "68719476736 is not a 36-bit number."
