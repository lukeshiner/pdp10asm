from unittest import mock

import pytest

from pdp10asm.passes import FirstPassAssembler
from pdp10asm.pseudo_operators import PseudoOperators
from pdp10asm.symbol_table import SymbolTable


@pytest.fixture
def mock_assembler():
    assembler = mock.Mock()
    assembler.symbol_table = SymbolTable()
    assembler.pseudo_operators = PseudoOperators(assembler)
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
    return mock.Mock(is_pseudo_operator=False, is_assignment=False)


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


def test_processs_line_handles_pseudo_operators(
    mock_handle_labels,
    mock_handle_assignments,
    mock_handle_pseudo_operator,
    first_pass_assembler,
    source_line,
):
    source_line.is_pseudo_operator = True
    first_pass_assembler.process_line(source_line)
    mock_handle_pseudo_operator.assert_called_once_with(source_line)
    mock_handle_labels.assert_not_called()
    mock_handle_assignments.assert_not_called()


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
