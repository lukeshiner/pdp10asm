from unittest import mock

import pytest

from pdp10asm.passes import FirstPassAssembler
from pdp10asm.symbol_table import SymbolTable


@pytest.fixture
def mock_assembler():
    assembler = mock.Mock()
    assembler.symbol_table = SymbolTable()
    return assembler


@pytest.fixture
def first_pass_assembler(mock_assembler):
    return FirstPassAssembler(assembler=mock_assembler)


@pytest.fixture
def mock_parser():
    with mock.patch("pdp10asm.passes.Parser") as m:
        yield m


@pytest.fixture
def source_line():
    return mock.Mock(
        is_pseudo_operator=False, is_assignment=False, memory_location_count=0
    )


@pytest.fixture
def mock_handle_labels(first_pass_assembler):
    first_pass_assembler.handle_labels = mock.Mock()
    return first_pass_assembler.handle_labels


@pytest.fixture
def mock_handle_assignments(first_pass_assembler):
    first_pass_assembler.handle_assignments = mock.Mock()
    return first_pass_assembler.handle_assignments


@pytest.fixture
def mock_handle_pseudo_operator(first_pass_assembler):
    first_pass_assembler.handle_pseudo_operator = mock.Mock()
    return first_pass_assembler.handle_pseudo_operator


@pytest.fixture
def mock_literal_value(first_pass_assembler):
    first_pass_assembler.literal_value = mock.Mock()
    return first_pass_assembler.literal_value


@pytest.fixture
def mock_twos_complement_value(first_pass_assembler):
    first_pass_assembler.twos_complement_value = mock.Mock(return_value=234)
    return first_pass_assembler.twos_complement_value


@pytest.fixture
def mock_add_instructions(first_pass_assembler):
    first_pass_assembler.add_instructions = mock.Mock()
    return first_pass_assembler.add_instructions


def test_process_line_handles_pseudo_operators(
    mock_handle_labels,
    mock_handle_assignments,
    mock_handle_pseudo_operator,
    first_pass_assembler,
    source_line,
    mock_add_instructions,
):
    source_line.is_pseudo_operator = True
    first_pass_assembler.process_line(source_line)
    mock_handle_pseudo_operator.assert_called_once_with(source_line)
    mock_handle_labels.assert_not_called()
    mock_handle_assignments.assert_not_called()
    mock_add_instructions.assert_not_called()


def test_process_line_calls_handle_labels(
    mock_handle_labels,
    mock_handle_assignments,
    mock_handle_pseudo_operator,
    first_pass_assembler,
    source_line,
):
    first_pass_assembler.process_line(source_line)
    mock_handle_labels.assert_called_once_with(source_line)


def test_process_line_calls_handle_assignments(
    mock_handle_labels,
    mock_handle_assignments,
    mock_handle_pseudo_operator,
    first_pass_assembler,
    source_line,
):
    source_line.is_assignment = True
    first_pass_assembler.process_line(source_line)
    mock_handle_assignments.assert_called_once_with(source_line)


def test_process_line_updates_program_counter(
    mock_handle_labels,
    mock_handle_assignments,
    mock_handle_pseudo_operator,
    first_pass_assembler,
    source_line,
):
    first_pass_assembler.program_counter = 10
    source_line.memory_location_count = 5
    first_pass_assembler.process_line(source_line)
    assert first_pass_assembler.program_counter == 15


@mock.patch("pdp10asm.passes.PseudoOperators")
def test_handle_pseudo_operator_with_first_pass_operator(
    mock_pseudo_operators, first_pass_assembler, source_line
):
    operator = mock.Mock(first_pass=True)
    mock_pseudo_operators.get_pseudo_op.return_value = operator
    first_pass_assembler.handle_pseudo_operator(source_line)
    mock_pseudo_operators.get_pseudo_op.assert_called_once_with(source_line.operator)
    operator.process.assert_called_once_with(
        assembler=first_pass_assembler.assembler, source_line=source_line
    )


@mock.patch("pdp10asm.passes.PseudoOperators")
def test_handle_pseudo_operator_with_non_first_pass_operator(
    mock_pseudo_operators, first_pass_assembler, source_line
):
    first_pass_assembler._handle_pseudo_operator = mock.Mock()
    operator = mock.Mock(first_pass=False)
    mock_pseudo_operators.get_pseudo_op.return_value = operator
    first_pass_assembler.handle_pseudo_operator(source_line)
    mock_pseudo_operators.get_pseudo_op.assert_called_once_with(source_line.operator)
    operator.process.assert_not_called()


def test_handle_labels(first_pass_assembler, source_line):
    source_line.labels = ["LABEL1", "LABEL2", "LABEL3"]
    first_pass_assembler.add_label = mock.Mock()
    first_pass_assembler.handle_labels(source_line)
    first_pass_assembler.add_label.assert_has_calls(
        (
            mock.call(label, source_line.source_line_number)
            for label in source_line.labels
        ),
        any_order=False,
    )


def test_add_label(mock_assembler, first_pass_assembler):
    first_pass_assembler.program_counter = 10
    first_pass_assembler.symbol_table = mock.Mock()
    source_line_number = 5
    first_pass_assembler.add_label("LABEL", source_line_number)
    first_pass_assembler.symbol_table.add_user_symbol.assert_called_once_with(
        symbol="LABEL", value=10, source_line=source_line_number
    )


def test_handle_assignment(
    mock_twos_complement_value, first_pass_assembler, source_line
):
    first_pass_assembler.symbol_table = mock.Mock()
    source_line.is_assignment = True
    first_pass_assembler.handle_assignments(source_line)
    mock_twos_complement_value.assert_called_once_with(source_line.assignment_value)
    first_pass_assembler.symbol_table.add_user_symbol.assert_called_once_with(
        symbol=source_line.assignment_symbol,
        value=mock_twos_complement_value.return_value,
        source_line=source_line.source_line_number,
    )


def test_handle_assignment_with_non_assignment(first_pass_assembler, source_line):
    first_pass_assembler.parse_expression = mock.Mock()
    first_pass_assembler.symbol_table = mock.Mock()
    source_line.is_assignment = False
    first_pass_assembler.handle_assignments(source_line)
    first_pass_assembler.parse_expression.assert_not_called()
    first_pass_assembler.symbol_table.add_user_symbol.assert_not_called()
