from unittest import mock

import pytest

import pdp10asm.pseudo_operators.pseudo_ops as po
from pdp10asm.exceptions import AssemblyError
from pdp10asm.pseudo_operators import PseudoOperators


@pytest.fixture
def mock_assembler():
    return mock.Mock(radix=8)


def test_pseudo_operators_has_instructions():
    assert PseudoOperators.instructions == {
        "LOC": po.Loc,
        "END": po.End,
        "TITLE": po.Title,
        "SUBTTLE": po.Subtitle,
        "RADIX": po.Radix,
        "EXP": po.Exp,
        "DEC": po.Dec,
        "OCT": po.Oct,
        "BYTE": po.Byte,
        "POINT": po.Point,
        "IOWD": po.Iowd,
        "XWD": po.Xwd,
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


def test_radix_instruction(mock_assembler):
    source_line = mock.Mock(arguments="10")
    po.Radix.process(mock_assembler, source_line)
    assert mock_assembler.radix == 10


@pytest.mark.parametrize("value", ("WORD", "50,20", "1", "11"))
def test_radix_instruction_with_invalid_value(value, mock_assembler):
    source_line = mock.Mock(arguments=value)
    with pytest.raises(AssemblyError):
        po.Radix.process(mock_assembler, source_line)
    assert mock_assembler.radix == 8


def test_exp_source_line_process():
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Exp.source_line_process(source_line)
    assert source_line.memory_location_count == 6


def test_exp_process(mock_assembler):
    mock_assembler.radix = 5
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Exp.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[1, 2, 3, 5, 7, 25]
    )


def test_dec_source_line_process():
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Dec.source_line_process(source_line)
    assert source_line.memory_location_count == 6


def test_dec_process(mock_assembler):
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Dec.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[1, 2, 3, 10, 12, 100]
    )


def test_oct_source_line_process():
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Oct.source_line_process(source_line)
    assert source_line.memory_location_count == 6


def test_oct_process(mock_assembler):
    source_line = mock.Mock(arguments="1,2,3,10,12,100")
    po.Oct.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[1, 2, 3, 8, 10, 64]
    )


@pytest.mark.parametrize(
    "length,values,expected",
    (
        (18, 4, 2),
        (18, 5, 3),
        (3, 12, 1),
        (3, 13, 2),
        (3, 24, 2),
        (3, 25, 3),
    ),
)
def test_byte_word_count(length, values, expected):
    assert po.Byte.word_count(length, values) == expected


def test_byte_source_line_process():
    source_line = mock.Mock(arguments="(18) 1,1,1,1")
    po.Byte.source_line_process(source_line)
    assert source_line.memory_location_count == 2


@pytest.mark.parametrize(
    "length,values,expected",
    (
        (18, [1, 1, 1, 1], [0o000001000001, 0o000001000001]),
        (18, [3, 3, 3, 3, 3], [0o000003000003, 0o000003000003, 0o000003000000]),
        (18, [0o7777777], [0o777777000000]),
        (3, [0o5, 0o4, 0o7, 0o12], [0o547200000000]),
    ),
)
def test_byte_get_binary_values(length, values, expected):
    assert po.Byte.get_binary_values(length, values) == expected


def test_byte_process(mock_assembler):
    source_line = mock.Mock(arguments="(18) 1,1,1,1+1")
    po.Byte.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[0o000001000001, 0o000001000002]
    )


@pytest.mark.parametrize(
    "argument,length,value",
    (
        ("(18) 1,2,3, 4", 18, ["1", "2", "3", "4"]),
        ("(3)1,2,3+5", 3, ["1", "2", "3+5"]),
    ),
)
def test_byte_parse_with_valid_argument(argument, length, value):
    assert po.Byte.parse(argument) == (length, value)


@pytest.mark.parametrize(
    "argument",
    (
        "18) 1,2,3, 4",
        "(18 1,2,3, 4",
        "18 1,2,3, 4",
        "18, 1,2,3, 4",
        "(0) 1,2,3, 4",
        "(37) 1,2,3, 4",
        "(WORD) 1,2,3, 4",
    ),
)
def test_byte_parse_with_invalid_argument(argument):
    with pytest.raises(AssemblyError):
        po.Byte.parse(argument)


def test_point_source_line_process():
    source_line = mock.Mock()
    po.Point.source_line_process(source_line)
    assert source_line.memory_location_count == 1


@pytest.mark.parametrize(
    "text,expected",
    (
        ("s, address, b", ("s", "address", "b")),
        ("s, address", ("s", "address", None)),
    ),
)
def test_point_parse_method(text, expected):
    po.Point.parse(text) == expected


@pytest.mark.parametrize("text", (("s"), ("s,address,b,c")))
def test_point_parse_method_with_invalid_value(text):
    with pytest.raises(AssemblyError) as e:
        po.Point.parse(text)
    assert (
        str(e.value) == "The POINT pseudo op is formatted (decimal, address, decimal)."
    )


def test_point_convert_byte_size():
    assert po.Point.convert_byte_size("12") == 12


@pytest.mark.parametrize("text", ("0", "37", "word"))
def test_point_convert_byte_size_with_invalid_value(text):
    with pytest.raises(AssemblyError) as e:
        po.Point.convert_byte_size(text)
    assert (
        str(e.value)
        == "The first argument to POINT must be a decimal integer between 1 and 36."
    )


@pytest.mark.parametrize(
    "text,expected",
    (
        ("12", 12),
        (None, 0),
    ),
)
def test_point_convert_position(text, expected):
    assert po.Point.convert_position(text) == expected


@pytest.mark.parametrize("text", ("0", "37", "word"))
def test_point_convert_position_with_invalid_value(text):
    with pytest.raises(AssemblyError) as e:
        po.Point.convert_position(text)
    assert (
        str(e.value)
        == "The third argument to POINT must be a decimal integer between 1 and 36."
    )


@pytest.mark.parametrize(
    "position,byte_size,address,expected",
    (
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (1, 0, 0, 0o010000000000),
        (0, 1, 0, 0o000100000000),
        (0, 0, 1, 0o000000000001),
        (1, 1, 1, 0o010100000001),
        (5, 5, 0o255, 0o050500000255),
        (36, 36, 0o47777777, 0o444447777777),
    ),
)
def test_point_create_point(position, byte_size, address, expected):
    assert (
        po.Point.create_point(byte_size=byte_size, position=position, address=address)
        == expected
    )


def test_point_process(mock_assembler):
    mock_assembler.symbol_table.get_symbol_value.return_value = 0o47777777
    source_line = mock.Mock(arguments="36,ADD,36")
    po.Point.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[0o444447777777]
    )


def test_iowd_source_line_process():
    source_line = mock.Mock()
    po.Iowd.source_line_process(source_line)
    assert source_line.memory_location_count == 1


def test_iowd_parse():
    assert po.Iowd.parse("ONE,TWO") == ("ONE", "TWO")


@pytest.mark.parametrize("value", ("ONE", "ONE,TWO,THREE"))
def test_iowd_parse_with_invalid_value(value):
    with pytest.raises(AssemblyError) as e:
        po.Iowd.parse(value)
    assert str(e.value) == "IOWD takes two arguments."


@mock.patch("pdp10asm.pseudo_operators.pseudo_ops.ExpressionParser")
def test_iowd_convert_counter(mock_expression_parser, mock_assembler):
    mock_expression_parser.return_value.as_half_word.return_value = 6
    returned_value = po.Iowd.convert_counter(mock_assembler, "text")
    mock_expression_parser.assert_called_once_with("text", mock_assembler)
    mock_expression_parser.return_value.as_half_word.assert_called_once_with(
        negative=True
    )
    assert (
        returned_value == mock_expression_parser.return_value.as_half_word.return_value
    )


@mock.patch("pdp10asm.pseudo_operators.pseudo_ops.ExpressionParser")
def test_iowd_convert_address(mock_expression_parser, mock_assembler):
    mock_expression_parser.return_value.as_half_word.return_value = 256
    returned_value = po.Iowd.convert_address(mock_assembler, "text")
    mock_expression_parser.assert_called_once_with("text", mock_assembler)
    mock_expression_parser.return_value.as_half_word.assert_called_once_with()
    assert returned_value == 255


def test_iowd_process(mock_assembler):
    source_line = mock.Mock(arguments="6,400")
    po.Iowd.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[0o777772000377]
    )


def test_xwd_source_line_process():
    source_line = mock.Mock()
    po.Xwd.source_line_process(source_line)
    assert source_line.memory_location_count == 1


def test_xwd_parse():
    assert po.Xwd.parse("ONE,TWO") == ("ONE", "TWO")


@pytest.mark.parametrize("value", ("ONE", "ONE,TWO,THREE"))
def test_xwd_parse_with_invalid_value(value):
    with pytest.raises(AssemblyError) as e:
        po.Xwd.parse(value)
    assert str(e.value) == "XWD takes two arguments."


@pytest.mark.parametrize(
    "left_text,right_text,expected",
    (
        ("1", "1", 0o000001000001),
        ("1+1", "2+2", 0o000002000004),
    ),
)
def test_xwd_get_value(left_text, right_text, expected, mock_assembler):
    assert po.Xwd.get_value(left_text, right_text, mock_assembler) == expected


def test_xwd_process(mock_assembler):
    source_line = mock.Mock(arguments="6,400")
    po.Xwd.process(mock_assembler, source_line)
    mock_assembler.current_pass.add_instructions.assert_called_once_with(
        source_line=source_line, binary_values=[0o000006000400]
    )
