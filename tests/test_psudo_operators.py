from unittest import mock

import pytest

import pdp10asm.pseudo_operators.pseudo_ops as po
from pdp10asm.pseudo_operators import PseudoOperators


@pytest.fixture
def mock_assembler():
    return mock.Mock()


def test_pseudo_operators_has_instructions():
    assert PseudoOperators.instructions == {
        "LOC": po.Loc,
        "END": po.End,
        "TITLE": po.Title,
        "SUBTTLE": po.Subtitle,
    }


@pytest.mark.parametrize(
    "word,expected",
    (
        ("LOC", True),
        ("loc", True),
        ("END", True),
        ("OTHER", False),
    ),
)
def test_is_pseudo_operator_method(word, expected):
    assert PseudoOperators.is_pseudo_op(word) is expected


@pytest.mark.parametrize(
    "word,expected",
    (
        ("LOC", po.Loc),
        ("loc", po.Loc),
        ("END", po.End),
        ("OTHER", None),
    ),
)
def test_get_pseudo_operator_method(word, expected):
    assert PseudoOperators.get_pseudo_op(word) is expected


def test_base_pseudo_op_raises(mock_assembler):
    with pytest.raises(NotImplementedError):
        po.PseudoOp.process(mock_assembler, mock.Mock())


def test_loc_instruction(mock_assembler):
    source_line = mock.Mock(arguments="500")
    po.Loc.process(mock_assembler, source_line)
    assert mock_assembler.current_pass.program_counter == 0o500


def test_end_instruction(mock_assembler):
    po.End.process(mock_assembler, mock.Mock())
    assert mock_assembler.current_pass.done is True


def test_title_instruction(mock_assembler):
    mock_assembler.program.title = "Untitled"
    source_line = mock.Mock(arguments="Hello World")
    po.Title.process(mock_assembler, source_line)
    assert mock_assembler.program.title == "Hello World"


def test_subtitle_instruction(mock_assembler):
    mock_assembler.program.subtitle = ""
    source_line = mock.Mock(arguments="Hello World")
    po.Subtitle.process(mock_assembler, source_line)
    assert mock_assembler.program.subtitle == "Hello World"
