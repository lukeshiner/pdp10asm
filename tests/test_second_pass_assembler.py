import types
from unittest import mock

import pytest

from pdp10asm.exceptions import AssemblyError
from pdp10asm.passes import SecondPassAssembler
from pdp10asm.symbol_table import SymbolTable


@pytest.fixture
def mock_assembler():
    assembler = mock.Mock(program={}, symbol_table=SymbolTable())

    return assembler


@pytest.fixture
def second_pass(mock_assembler):
    return SecondPassAssembler(assembler=mock_assembler)


@pytest.fixture
def mock_parser():
    with mock.patch("pdp10asm.passes.Parser") as m:
        yield m


@pytest.fixture
def source_line():
    return mock.Mock(is_assignment=False, is_pseudo_operator=False)


def test_base_assmbler_pass_has_assembler(second_pass, mock_assembler):
    assert second_pass.assembler == mock_assembler


def test_second_pass_assembler_pass_has_symbol_table(mock_assembler):
    second_pass = SecondPassAssembler(assembler=mock_assembler)
    assert second_pass.symbol_table == mock_assembler.symbol_table


def test_second_pass_assembler_pass_has_pseudo_operators(mock_assembler, second_pass):
    assert second_pass.pseudo_operators == mock_assembler.pseudo_operators


def test_second_pass_assembler_pass_has_program_counter(second_pass):
    assert second_pass.program_counter == 0


def test_second_pass_assembler_pass_has_source_line_number(second_pass):
    assert second_pass.source_line_number == 0


def test_second_pass_assembler_pass_has_done_property(second_pass):
    assert second_pass.done is False


def test_second_pass_assembler_pass_has_operations_property(second_pass):
    for key, value in second_pass.operations.items():
        assert isinstance(key, str)
        assert isinstance(value, types.FunctionType)


@pytest.fixture
def mock_handle_pseudo_operator(second_pass):
    second_pass.handle_pseudo_operator = mock.Mock()
    return second_pass.handle_pseudo_operator


@pytest.fixture
def mock_assemble_line(second_pass):
    second_pass.assemble_line = mock.Mock()
    return second_pass.assemble_line


def test_process_line_ignores_assignments(
    source_line, mock_handle_pseudo_operator, mock_assemble_line, second_pass
):
    source_line.is_assignment = True
    second_pass.process_line(source_line)
    mock_handle_pseudo_operator.assert_not_called()
    mock_assemble_line.assert_not_called()
    assert second_pass.program_counter == 0


def test_process_line_passes_input_to_assemble_line_when_not_pseudo_operator_or_assignment_and_is_assemblable(
    source_line, mock_handle_pseudo_operator, mock_assemble_line, second_pass
):
    source_line.is_assemblable = True
    second_pass.process_line(source_line)
    mock_assemble_line.assert_called_once_with(source_line)
    mock_handle_pseudo_operator.assert_not_called()


def test_process_line_updates_program_when_not_pseudo_operator_or_assignment_and_assemblable(
    source_line, mock_assemble_line, second_pass
):
    source_line.is_assemblable = True
    second_pass.program_counter = 4
    second_pass.process_line(source_line)
    assert second_pass.assembler.program == {4: mock_assemble_line.return_value}


def test_process_line_does_not_update_program_when_not_assemblable(
    source_line, mock_assemble_line, second_pass
):
    source_line.is_assemblable = False
    second_pass.process_line(source_line)
    mock_assemble_line.assert_not_called()
    assert second_pass.assembler.program == {}


def test_process_line_does_not_handle_assmbler_instruction_when_not_pseudo_operator(
    source_line, mock_handle_pseudo_operator, mock_assemble_line, second_pass
):
    second_pass.process_line(source_line)
    mock_handle_pseudo_operator.assert_not_called()


def test_process_line_calls_handle_assmbler_instruction_when_pseudo_operator(
    source_line,
    mock_handle_pseudo_operator,
    mock_assemble_line,
    second_pass,
):
    source_line.is_pseudo_operator = True
    second_pass.process_line(source_line)
    mock_handle_pseudo_operator.assert_called_once_with(source_line)


def test_process_line_does_not_call_assemble_line_when_pseudo_operator(
    source_line,
    mock_handle_pseudo_operator,
    mock_assemble_line,
    second_pass,
):
    source_line.is_pseudo_operator = True
    second_pass.process_line(source_line)
    mock_assemble_line.assert_not_called()


@pytest.fixture
def mock_symbol_table(second_pass):
    second_pass.symbol_table = mock.Mock()
    return second_pass.symbol_table


@pytest.fixture
def mock_parse_expression(second_pass):
    second_pass.parse_expression = mock.Mock(return_value=234)
    return second_pass.parse_expression


@pytest.fixture
def mock_symbol_value(second_pass):
    second_pass.symbol_value = mock.Mock(return_value=634)
    return second_pass.symbol_value


@pytest.fixture
def mock_primary_operand_value(second_pass):
    second_pass.primary_operand_value = mock.Mock(return_value=457)
    return second_pass.primary_operand_value


@pytest.fixture
def mock_io_operand_value(second_pass):
    second_pass.io_operand_value = mock.Mock(return_value=457)
    return second_pass.io_operand_value


def test_assemble_line_returns_parsed_expression_when_passed_value(
    mock_symbol_table,
    mock_parse_expression,
    mock_symbol_value,
    mock_primary_operand_value,
    mock_io_operand_value,
    second_pass,
    source_line,
):
    source_line.is_value = True
    return_value = second_pass.assemble_line(source_line)
    mock_parse_expression.assert_called_once_with(source_line.value)
    assert return_value == mock_parse_expression.return_value


def test_assemble_line_with_primary_instruction(
    mock_symbol_table,
    mock_parse_expression,
    mock_symbol_value,
    mock_primary_operand_value,
    mock_io_operand_value,
    second_pass,
    source_line,
):
    source_line.is_primary_instruction = True
    return_value = second_pass.assemble_line(source_line)
    mock_primary_operand_value.assert_called_once_with(source_line)
    assert (
        return_value
        == mock_symbol_value.return_value | mock_primary_operand_value.return_value
    )


def test_assemble_line_with_io_instruction(
    mock_symbol_table,
    mock_parse_expression,
    mock_symbol_value,
    mock_primary_operand_value,
    mock_io_operand_value,
    second_pass,
    source_line,
):
    source_line.is_io_instruction = True
    return_value = second_pass.assemble_line(source_line)
    mock_io_operand_value.assert_called_once_with(source_line)
    assert (
        return_value
        == mock_symbol_value.return_value | mock_io_operand_value.return_value
    )


def test_assemble_line_with_invalid_instruction(
    mock_symbol_table,
    mock_parse_expression,
    mock_symbol_value,
    mock_primary_operand_value,
    mock_io_operand_value,
    second_pass,
    source_line,
):
    source_line.text = "text"
    with pytest.raises(AssemblyError) as exc_info:
        second_pass.assemble_line(source_line)
    assert str(exc_info.value) == "Unable to parse line 'text'"


@pytest.mark.parametrize(
    "value,expected",
    (
        (0, 0),
        (1, 0o000040000000),
        (2, 0o000100000000),
        (3, 0o000140000000),
        (4, 0o000200000000),
        (5, 0o000240000000),
        (6, 0o000300000000),
        (7, 0o000340000000),
        (8, 0o000400000000),
        (9, 0o000440000000),
        (10, 0o000500000000),
        (11, 0o000540000000),
        (12, 0o000600000000),
        (13, 0o000640000000),
        (14, 0o000700000000),
        (15, 0o000740000000),
    ),
)
def test_accumulator_value(value, expected, second_pass):
    second_pass.validate_accumulator_value = mock.Mock()
    second_pass.symbol_or_value = mock.Mock(return_value=value)
    assert second_pass.accumulator_value("AC") == expected
    second_pass.symbol_or_value.assert_called_once_with("AC")
    second_pass.validate_accumulator_value.assert_called_once_with(
        second_pass.symbol_or_value.return_value
    )


def test_accumulator_value_with_none(second_pass):
    second_pass.validate_accumulator_value = mock.Mock()
    second_pass.symbol_or_value = mock.Mock()
    assert second_pass.accumulator_value(None) == 0
    second_pass.symbol_or_value.assert_not_called
    second_pass.validate_accumulator_value.assert_not_called()


def test_validate_accumulator_value_with_too_large_value(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_accumulator_value(16)


def test_validate_accumulator_value_with_too_small_value(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_accumulator_value(-1)


def test_validate_accumulator_value_with_valid_value(second_pass):
    second_pass.validate_accumulator_value(15)


def test_address_value(second_pass):
    second_pass.validate_address = mock.Mock()
    second_pass.symbol_or_value = mock.Mock(return_value=127)
    assert second_pass.address_value("AC") == second_pass.symbol_or_value.return_value
    second_pass.symbol_or_value.assert_called_once_with("AC")
    second_pass.validate_address.assert_called_once_with(
        second_pass.symbol_or_value.return_value
    )


def test_validate_address(second_pass):
    for i in range(0o777777):
        second_pass.validate_address(i)
    with pytest.raises(AssemblyError):
        second_pass.validate_address(0o1000000)
    with pytest.raises(AssemblyError):
        second_pass.validate_address(-1)


def test_validate_index_register_word_with_too_large_value(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_index_register_value(16)


def test_validate_index_register_word_with_too_small_value(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_index_register_value(-1)


def test_validate_index_register_word_with_valid_value(second_pass):
    second_pass.validate_index_register_value(15)


@pytest.mark.parametrize(
    "ac,index,indirect,mem,expected",
    (
        (0, 0, False, 0, 0),
        (0o1, 0o30, False, 0o200, 0o231),
        (0o1, 0o30, True, 0o200, 0o20000231),
    ),
)
def test_primary_operand_value(
    ac, index, indirect, mem, expected, second_pass, source_line
):
    second_pass.accumulator_value = mock.Mock(return_value=ac)
    source_line.is_indirect = indirect
    second_pass.address_value = mock.Mock(return_value=mem)
    second_pass.index_register_value = mock.Mock(return_value=index)
    assert second_pass.primary_operand_value(source_line) == expected
    second_pass.accumulator_value.assert_called_once_with(source_line.accumulator)
    second_pass.index_register_value.assert_called_once_with(source_line.index_register)
    second_pass.address_value.assert_called_once_with(source_line.memory_address)


@pytest.mark.parametrize(
    "dev,index,indirect,mem,expected",
    (
        (0, 0, False, 0, 0),
        (0o1, 0o30, False, 0o200, 0o231),
        (0o1, 0o30, True, 0o200, 0o20000231),
    ),
)
def test_io_operand_value(
    dev, index, indirect, mem, expected, second_pass, source_line
):
    second_pass.device_id_value = mock.Mock(return_value=dev)
    source_line.is_indirect = indirect
    second_pass.address_value = mock.Mock(return_value=mem)
    second_pass.index_register_value = mock.Mock(return_value=index)
    assert second_pass.io_operand_value(source_line) == expected
    second_pass.device_id_value.assert_called_once_with(source_line.device_id)
    second_pass.index_register_value.assert_called_once_with(source_line.index_register)
    second_pass.address_value.assert_called_once_with(source_line.memory_address)


@pytest.mark.parametrize(
    "value,expected",
    (
        (0, 0),
        (1, 0o000001000000),
        (2, 0o000002000000),
        (3, 0o000003000000),
        (4, 0o000004000000),
        (5, 0o000005000000),
        (6, 0o000006000000),
        (7, 0o000007000000),
        (8, 0o000010000000),
        (9, 0o000011000000),
        (10, 0o000012000000),
        (11, 0o000013000000),
        (12, 0o000014000000),
        (13, 0o000015000000),
        (14, 0o000016000000),
        (15, 0o000017000000),
    ),
)
def test_index_register_value(value, expected, second_pass):
    second_pass.validate_index_register_value = mock.Mock()
    second_pass.symbol_or_value = mock.Mock(return_value=value)
    assert second_pass.index_register_value("AC") == expected
    second_pass.symbol_or_value.assert_called_once_with("AC")
    second_pass.validate_index_register_value.assert_called_once_with(
        second_pass.symbol_or_value.return_value
    )


def test_index_register_value_with_none(second_pass):
    second_pass.validate_index_register_value = mock.Mock()
    second_pass.symbol_or_value = mock.Mock()
    assert second_pass.index_register_value(None) == 0
    second_pass.symbol_or_value.assert_not_called
    second_pass.validate_index_register_value.assert_not_called()


def test_device_id_value(second_pass):
    second_pass.validate_device_id = mock.Mock()
    second_pass.symbol_or_value = mock.Mock(return_value=0o104)
    assert second_pass.device_id_value("TTY,12") == 0o010400000000
    second_pass.symbol_or_value.assert_called_once_with("TTY,12")
    second_pass.validate_device_id.assert_called_once_with(
        second_pass.symbol_or_value.return_value
    )


def test_device_id_value_with_none(second_pass):
    second_pass.validate_device_id = mock.Mock()
    second_pass.symbol_or_value = mock.Mock()
    assert second_pass.device_id_value(None) == 0
    second_pass.symbol_or_value.assert_not_called
    second_pass.validate_device_id.assert_not_called()


def test_validate_device_id_does_not_raise_for_valid_id(second_pass):
    second_pass.validate_device_id(0o104)


def test_validate_device_id_raises_if_last_bits_of_id_are_not_zero(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_device_id(0o105)


def test_validate_device_id_raises_if_too_large(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_device_id(0o1000)


def test_validate_device_id_raises_if_too_small(second_pass):
    with pytest.raises(AssemblyError):
        second_pass.validate_device_id(-1)
