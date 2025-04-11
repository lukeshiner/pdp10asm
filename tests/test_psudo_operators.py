from unittest import mock

import pytest

from pdp10asm.pseudo_operators import PseudoOperators


@pytest.fixture
def mock_assembler():
    return mock.Mock()


@pytest.fixture
def pseudo_operators(mock_assembler):
    return PseudoOperators(assembler=mock_assembler)


def test_pseudo_operators_has_instructions(pseudo_operators):
    assert isinstance(pseudo_operators.instructions, dict)


def test_pseudo_operators_has_assembler(mock_assembler, pseudo_operators):
    assert pseudo_operators.assembler == mock_assembler


@pytest.mark.parametrize(
    "word,expected",
    (
        ("LOC", True),
        ("loc", True),
        ("END", True),
        ("OTHER", False),
    ),
)
def test_is_pseudo_operator_method(word, expected, pseudo_operators):
    assert pseudo_operators.is_pseudo_operator(word) is expected


def test_loc_instruction(mock_assembler, pseudo_operators):
    pseudo_operators.loc([500])
    assert mock_assembler.current_pass.program_counter == 500


def test_end_instruction(mock_assembler, pseudo_operators):
    pseudo_operators.end(None)
    assert mock_assembler.current_pass.done is True


def test_process_instruction(pseudo_operators):
    word = "FOO"
    method = mock.Mock()
    pseudo_operators.instructions[word] = method
    pseudo_operators.process_instruction(instruction_word=word, values=[500])
    method.assert_called_once_with([500])
