from unittest import mock

import pytest

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
def mock_literal_value(base_pass):
    base_pass.literal_value = mock.Mock()
    return base_pass.literal_value


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


def test_process_line_raises_not_implemented(base_pass):
    with pytest.raises(NotImplementedError):
        base_pass.process_line([])


def test_run_method(base_pass):
    base_pass.process_line = mock.Mock()
    base_pass.assembler.program.source_lines = [mock.Mock(is_empty=False)] * 3
    base_pass.run()
    base_pass.process_line.assert_has_calls(
        (
            mock.call(source_line)
            for source_line in base_pass.assembler.program.source_lines
        ),
        any_order=False,
    )


def test_run_method_skips_empty_instruction(base_pass):
    base_pass.process_line = mock.Mock()
    base_pass.assembler.program.source_lines = [
        mock.Mock(is_empty=False),
        mock.Mock(is_empty=True),
        mock.Mock(is_empty=False),
    ]
    base_pass.run()
    base_pass.process_line.assert_has_calls(
        (
            mock.call(base_pass.assembler.program.source_lines[0]),
            mock.call(base_pass.assembler.program.source_lines[2]),
        ),
        any_order=False,
    )


def test_run_method_stops_when_done_is_true(base_pass):
    base_pass.done = True
    base_pass.process_line = mock.Mock()
    base_pass.assembler.program.source_lines = [mock.Mock(is_empty=False)] * 3
    base_pass.run()
    base_pass.process_line.assert_not_called()


def test_run_method_does_not_increment_program_counter_when_source_line_is_not_assemblable(
    base_pass,
):
    base_pass.program_counter = 5
    base_pass.process_line = mock.Mock()
    base_pass.assembler.program.source_lines = [
        mock.Mock(is_empty=False, is_assemblable=False)
    ]
    base_pass.run()
    base_pass.process_line.assert_called_once_with(
        base_pass.assembler.program.source_lines[0]
    )
    assert base_pass.program_counter == 5


def test_run_method_increments_program_counter_when_source_line_is_assemblable(
    base_pass,
):
    base_pass.program_counter = 5
    base_pass.process_line = mock.Mock()
    base_pass.assembler.program.source_lines = [
        mock.Mock(is_empty=False, is_assemblable=True)
    ]
    base_pass.run()
    base_pass.process_line.assert_called_once_with(
        base_pass.assembler.program.source_lines[0]
    )
    assert base_pass.program_counter == 6


def test_handle_pseudo_operator_method(
    base_pass, mock_pseudo_operators, mock_literal_value
):
    source_line = mock.Mock(operator="INST", arguments="500 250")
    base_pass.handle_pseudo_operator(source_line)
    mock_literal_value.assert_has_calls(
        (
            mock.call("500"),
            mock.call("250"),
        ),
        any_order=False,
    )
    mock_pseudo_operators.process_instruction.assert_called_once_with(
        instruction_word="INST",
        values=[
            mock_literal_value.return_value,
            mock_literal_value.return_value,
        ],
    )


def test_symbol_value(base_pass, symbol):
    base_pass.symbol_table.add_user_symbol(symbol, 10, 10)
    assert base_pass.symbol_value(symbol) == 10


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


@mock.patch("pdp10asm.passes.ExpressionParser")
def test_literal_value(mock_ExpressionParser, base_pass):
    return_value = base_pass.literal_value("text")
    mock_ExpressionParser.assert_called_once_with("text", base_pass.assembler)
    mock_ExpressionParser.return_value.as_literal.assert_called_once_with()
    assert return_value == mock_ExpressionParser.return_value.as_literal.return_value


@mock.patch("pdp10asm.passes.ExpressionParser")
def test_twos_complement_value(mock_ExpressionParser, base_pass):
    return_value = base_pass.twos_complement_value("text")
    mock_ExpressionParser.assert_called_once_with("text", base_pass.assembler)
    mock_ExpressionParser.return_value.as_twos_complement.assert_called_once_with()
    assert (
        return_value
        == mock_ExpressionParser.return_value.as_twos_complement.return_value
    )
