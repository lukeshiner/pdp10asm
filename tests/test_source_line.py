from unittest import mock

import pytest

from pdp10asm.assembler import PDP10Assembler
from pdp10asm.exceptions import AssemblyError
from pdp10asm.source_line import SourceLine


@pytest.fixture
def text():
    return "some text"


@pytest.fixture
def source_line_number():
    return 5


@pytest.fixture
def source_line(text, source_line_number):
    return SourceLine(
        assembler=mock.Mock(), source_line_number=source_line_number, text=text
    )


def test_has_source_line_number(source_line):
    assert source_line.source_line_number == source_line.source_line_number


@pytest.mark.parametrize(
    "string,return_value,comment",
    (
        ("", "", None),
        ("FOO BAR", "FOO BAR", None),
        ("FOO", "FOO", None),
        ("FOO BAR ; some comment", "FOO BAR", "some comment"),
        (";", "", ""),
        ("; some comment", "", "some comment"),
        ("   ;   some comment", "", "some comment"),
    ),
)
def test_read_comment(string, return_value, comment, source_line):
    assert source_line._read_comment(string) == return_value
    assert source_line.comment == comment


@pytest.mark.parametrize(
    "string,labels,return_value",
    (
        ("", [], ""),
        ("LABEL:", ["LABEL"], ""),
        ("HELLO:", ["HELLO"], ""),
        (".LAB:", [".LAB"], ""),
        ("L.AB:", ["L.AB"], ""),
        ("LAB.:", ["LAB."], ""),
        ("%LAB:", ["%LAB"], ""),
        ("LAB%:", ["LAB%"], ""),
        ("LA%B:", ["LA%B"], ""),
        ("F500:", ["F500"], ""),
        ("LABEL: more text", ["LABEL"], "more text"),
        ("LABEL: LABEL2: more text", ["LABEL", "LABEL2"], "more text"),
        ("LABEL:LABEL2: more text", ["LABEL", "LABEL2"], "more text"),
    ),
)
def test_read_labels(string, labels, return_value, source_line):
    assert source_line._read_labels(string) == return_value
    assert source_line.labels == labels


def test_read_labels_sets_instruction_text(source_line):
    source_line._read_labels("LABEL: MOV 200")
    assert source_line.instruction_text == "MOV 200"


def test_read_assignment_with_assignment(source_line):
    text = "A= B"
    assert source_line._read_assignment(text) == ""
    assert source_line.is_assignment is True
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol == "A"
    assert source_line.assignment_value == "B"


def test_read_assignment_with_non_assignment(source_line):
    text = "A: B"
    assert source_line._read_assignment(text) == text
    assert source_line.is_assignment is False
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None


def test_read_assignment_with_empty_string(source_line):
    assert source_line._read_assignment("") == ""
    assert source_line.is_assignment is False
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None


@pytest.mark.parametrize(
    "string,symbol,value",
    (
        ("A=B", "A", "B"),
        ("A= B", "A", "B"),
        ("LABEL= VALUE WORDS", "LABEL", "VALUE WORDS"),
    ),
)
def test_read_assignment_with_valid_assignment(string, symbol, value, source_line):
    assert source_line._read_assignment(string) == ""
    assert source_line.assignment_symbol == symbol
    assert source_line.assignment_value == value


@pytest.mark.parametrize(
    "string,",
    (("A="), ("A= "), ("=B"), (" = B")),
)
def test_read_assignment_with_invalid_assignment(string, source_line):
    with pytest.raises(AssemblyError) as exc_info:
        source_line._read_assignment(string)
    assert str(exc_info.value) == f"Invalid assignment {string!r}."


@pytest.mark.parametrize(
    "string,expected",
    (
        ("A=B", True),
        ("A= B", True),
        ("A= B=", True),
        ("A = B", False),
    ),
)
def test_read_assignment_finds_valid_labels(string, expected, source_line):
    source_line._read_assignment(string)
    assert source_line.is_assignment is expected


@pytest.mark.parametrize(
    "string,error_text",
    (
        ("500:", "500"),
        ("TTY,50:", "TTY,50"),
        ("AB@C:", "AB@C"),
        ("LABEL:AB@C:", "AB@C"),
    ),
)
def test_read_labels_raises_for_invalid_label(string, error_text, source_line):
    with pytest.raises(AssemblyError) as exc_info:
        source_line._read_labels(string)
    assert str(exc_info.value) == f"Invalid label {error_text!r}."


@pytest.mark.parametrize(
    "string,operator,return_value",
    (
        ("", None, ""),
        ("MOVE AC0,@13", "MOVE", "AC0,@13"),
        ("BYTE 890 3993 288", "BYTE", "890 3993 288"),
        ("7000", "7000", ""),
    ),
)
def test_read_operator(string, operator, return_value, source_line):
    assert source_line._read_operator(string) == return_value
    assert source_line.operator == operator


def test_parse_instruction_type_with_no_operator(source_line):
    source_line.operator = None
    source_line._parse_instruction_type("")
    assert source_line.is_pseudo_operator is False
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assemblable is False
    assert source_line.is_value is False


def test_parse_instruction_type_with_pseudo_operator(source_line):
    source_line.operator = "text"
    source_line.assembler.pseudo_operators.is_pseudo_operator.return_value = True
    source_line._parse_instruction_type("")
    assert source_line.is_pseudo_operator is True
    assert source_line.is_assignment is False
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assemblable is False
    assert source_line.is_value is False


def test_parse_instruction_type_with_primary_instruction(source_line):
    source_line.operator = "text"
    source_line.assembler.pseudo_operators.is_pseudo_operator.return_value = False
    source_line.assembler.symbol_table.is_primary_instruction_symbol.return_value = True
    source_line._parse_instruction_type("")
    assert source_line.is_pseudo_operator is False
    assert source_line.is_assignment is False
    assert source_line.is_instruction is True
    assert source_line.is_primary_instruction is True
    assert source_line.is_io_instruction is False
    assert source_line.is_assemblable is True
    assert source_line.is_value is False


def test_parse_instruction_type_with_io_instruction(source_line):
    source_line.operator = "text"
    source_line.assembler.pseudo_operators.is_pseudo_operator.return_value = False
    source_line.assembler.symbol_table.is_primary_instruction_symbol.return_value = (
        False
    )
    source_line.assembler.symbol_table.is_io_instruction_symbol.return_value = True
    source_line._parse_instruction_type("")
    assert source_line.is_pseudo_operator is False
    assert source_line.is_assignment is False
    assert source_line.is_instruction is True
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is True
    assert source_line.is_assemblable is True
    assert source_line.is_value is False


def test_parse_instruction_type_with_value(source_line):
    source_line.operator = "text"
    source_line.assembler.pseudo_operators.is_pseudo_operator.return_value = False
    source_line.assembler.symbol_table.is_primary_instruction_symbol.return_value = (
        False
    )
    source_line.assembler.symbol_table.is_io_instruction_symbol.return_value = False
    source_line._parse_instruction_type("")
    assert source_line.is_pseudo_operator is False
    assert source_line.is_assignment is False
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assemblable is True
    assert source_line.is_value is True


def test_parse_instruction_type_with_invalid_value(source_line):
    source_line.operator = "text"
    source_line.assembler.pseudo_operators.is_pseudo_operator.return_value = False
    source_line.assembler.symbol_table.is_primary_instruction_symbol.return_value = (
        False
    )
    source_line.assembler.symbol_table.is_io_instruction.return_value = False
    with pytest.raises(AssemblyError) as exc_info:
        source_line._parse_instruction_type("invalid")
    assert str(exc_info.value) == "Unable to parse 'text'."


@pytest.fixture
def mock_read_comment(source_line):
    source_line._read_comment = mock.Mock()
    return source_line._read_comment


@pytest.fixture
def mock_read_labels(source_line):
    source_line._read_labels = mock.Mock()
    return source_line._read_labels


@pytest.fixture
def mock_read_assignment(source_line):
    source_line._read_assignment = mock.Mock()
    return source_line._read_assignment


@pytest.fixture
def mock_read_operator(source_line):
    source_line._read_operator = mock.Mock()
    return source_line._read_operator


@pytest.fixture
def mock_parse_instruction_type(source_line):
    source_line._parse_instruction_type = mock.Mock()
    return source_line._parse_instruction_type


@pytest.fixture
def mock_parse_arguments(source_line):
    source_line._parse_arguments = mock.Mock()
    return source_line._parse_arguments


def test_read_text_calls_read_comment(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.read_text()
    mock_read_comment.assert_called_once_with(text)


def test_read_text_calls_read_labels(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.read_text()
    mock_read_labels.assert_called_once_with(mock_read_comment.return_value)


def test_read_text_calls_read_assignment(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.read_text()
    mock_read_assignment.assert_called_once_with(mock_read_labels.return_value)


def test_read_text_calls_read_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.read_text()
    mock_read_operator.assert_called_once_with(mock_read_assignment.return_value)


def test_read_text_does_not_call_read_operator_with_assignment(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.is_assignment = True
    source_line.read_text()
    mock_read_operator.assert_not_called()


def test_read_text_does_not_call_parse_instruction_type_with_non_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.operator = None
    source_line.read_text()
    mock_parse_instruction_type.assert_not_called()


def test_read_text_does_not_call_parse_instruction_type_with_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.operator = "text"
    source_line.read_text()
    mock_parse_instruction_type.assert_called_once_with(mock_read_operator.return_value)


def test_read_text_does_not_call_parse_arguments_with_non_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.operator = None
    source_line.read_text()
    mock_parse_arguments.assert_not_called()


def test_read_text_does_not_call_parse_arguments_with_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.operator = "text"
    source_line.read_text()
    mock_parse_arguments.assert_called_once_with(mock_read_operator.return_value)


def test_read_text_raises_for_invalid_operator(
    mock_read_comment,
    mock_read_labels,
    mock_read_assignment,
    mock_read_operator,
    mock_parse_instruction_type,
    mock_parse_arguments,
    source_line,
    text,
):
    source_line.operator = "text"
    mock_parse_arguments.side_effect = Exception()
    mock_read_operator.return_value = "invalid text"
    with pytest.raises(AssemblyError) as e:
        source_line.read_text()
    assert str(e.value) == "Unable to parse argument 'invalid text'."


@pytest.fixture
def mock_parse_primary_operand(source_line):
    source_line._parse_primary_operand = mock.Mock()
    return source_line._parse_primary_operand


@pytest.fixture
def mock_parse_io_operand(source_line):
    source_line._parse_io_operand = mock.Mock()
    return source_line._parse_io_operand


@pytest.fixture
def mock_parse_value(source_line):
    source_line._parse_value = mock.Mock()
    return source_line._parse_value


def test_parse_arguments_with_pseudo_operator(
    mock_parse_primary_operand,
    mock_parse_io_operand,
    mock_parse_value,
    source_line,
    text,
):
    source_line.is_pseudo_operator = True
    source_line._parse_arguments(text)
    assert source_line.arguments == text
    mock_parse_primary_operand.assert_not_called()
    mock_parse_io_operand.assert_not_called()
    mock_parse_value.assert_not_called()


def test_parse_arguments_with_primary_instruction(
    mock_parse_primary_operand,
    mock_parse_io_operand,
    mock_parse_value,
    source_line,
    text,
):
    source_line.is_primary_instruction = True
    source_line._parse_arguments(text)
    assert source_line.arguments is None
    mock_parse_primary_operand.assert_called_once_with(text)
    mock_parse_io_operand.assert_not_called()
    mock_parse_value.assert_not_called()


def test_parse_arguments_with_io_instruction(
    mock_parse_primary_operand,
    mock_parse_io_operand,
    mock_parse_value,
    source_line,
    text,
):
    source_line.is_io_instruction = True
    source_line._parse_arguments(text)
    assert source_line.arguments is None
    mock_parse_primary_operand.assert_not_called()
    mock_parse_io_operand.assert_called_once_with(text)
    mock_parse_value.assert_not_called()


def test_parse_arguments_with_value(
    mock_parse_primary_operand,
    mock_parse_io_operand,
    mock_parse_value,
    source_line,
    text,
):
    source_line.is_value = True
    source_line._parse_arguments(text)
    assert source_line.arguments is None
    mock_parse_primary_operand.assert_not_called()
    mock_parse_io_operand.assert_not_called()
    mock_parse_value.assert_called_once_with(text)


def test_parse_arguments_with_invalid_value(
    mock_parse_primary_operand,
    mock_parse_io_operand,
    mock_parse_value,
    source_line,
    text,
):
    with pytest.raises(AssemblyError) as exc_info:
        source_line._parse_arguments("")
    assert str(exc_info.value) == "Statement not understood ''."
    assert source_line.arguments is None
    mock_parse_primary_operand.assert_not_called()
    mock_parse_io_operand.assert_not_called()
    mock_parse_value.assert_not_called()


def test_parse_value(source_line):
    text = "7000"
    assert source_line._parse_value(text) == text


@pytest.mark.parametrize(
    "string,ac,index,memory,indirect",
    (
        ("100", None, None, "100", False),
        ("LABEL", None, None, "LABEL", False),
        ("0", None, None, "0", False),
        ("0,", "0", None, "0", False),
        (",0", None, None, "0", False),
        ("0,0", "0", None, "0", False),
        ("0,0(0)", "0", "0", "0", False),
        ("AC,MEM(INDEX)", "AC", "INDEX", "MEM", False),
        ("AC,(INDEX)", "AC", "INDEX", "0", False),
        ("@100", None, None, "100", True),
        ("@LABEL", None, None, "LABEL", True),
        ("@0", None, None, "0", True),
        ("0,@", "0", None, "0", True),
        (",@0", None, None, "0", True),
        ("0,@0", "0", None, "0", True),
        ("0,@0(0)", "0", "0", "0", True),
        ("AC,@MEM(INDEX)", "AC", "INDEX", "MEM", True),
        ("AC,@(INDEX)", "AC", "INDEX", "0", True),
    ),
)
def test_parse_operand(string, ac, index, memory, indirect, source_line):
    accumulator, index_register, memory_address, is_indirect = (
        source_line._parse_operand(string)
    )
    assert accumulator == ac
    assert index_register == index
    assert memory_address == memory
    assert is_indirect is indirect


@pytest.fixture
def ac():
    return mock.Mock()


@pytest.fixture
def index():
    return mock.Mock()


@pytest.fixture
def memory():
    return mock.Mock()


@pytest.fixture
def indirect():
    return mock.Mock()


@pytest.fixture
def mock_parse_operand(source_line, ac, index, memory, indirect):
    source_line._parse_operand = mock.Mock(return_value=(ac, index, memory, indirect))
    return source_line._parse_operand


def test_parse_primary_operand(
    text, mock_parse_operand, ac, index, memory, indirect, source_line
):
    source_line._parse_primary_operand(text)
    mock_parse_operand.assert_called_once_with(text)
    assert source_line.accumulator == ac
    assert source_line.index_register == index
    assert source_line.memory_address == memory
    assert source_line.is_indirect == indirect
    assert source_line.device_id is None


def test_parse_io_operand(
    text, mock_parse_operand, ac, index, memory, indirect, source_line
):
    source_line._parse_io_operand(text)
    mock_parse_operand.assert_called_once_with(text)
    assert source_line.device_id == ac
    assert source_line.index_register == index
    assert source_line.memory_address == memory
    assert source_line.is_indirect == indirect
    assert source_line.accumulator is None


@pytest.mark.parametrize(
    "word,expected",
    (
        ("HELLO", True),
        ("500", False),
        ("TTY,50", False),
        ("F500", True),
        ("AB@C", False),
        ("$LABEL", True),
        ("LABEL$", True),
        ("LA$BLE", True),
        (".LAB", True),
        ("L.AB", True),
        ("LAB.", True),
        ("%LAB", True),
        ("LAB%", True),
        ("LA%B", True),
        (".", False),
    ),
)
def test_is_symbol(word, expected):
    assert SourceLine.is_symbol(word) is expected


@pytest.fixture
def assembler(text):
    return PDP10Assembler(text)


@pytest.mark.integration_test
def test_source_line_with_pseudo_operator(assembler):
    text = "        LOC 100   ;  comment"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_pseudo_operator is True
    assert source_line.operator == "LOC"
    assert source_line.arguments == "100"
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.is_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.accumulator is None
    assert source_line.index_register is None
    assert source_line.memory_address is None
    assert source_line.device_id is None
    assert source_line.is_indirect is False
    assert source_line.labels == []
    assert source_line.comment == "comment"


@pytest.mark.integration_test
def test_source_line_with_instruction(assembler):
    text = "LABEL1:LABEL2: LABEL3:    MOVE AC1,@MEM(INDEX)  ;  Some Words"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_instruction is True
    assert source_line.is_primary_instruction is True
    assert source_line.is_io_instruction is False
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator == "MOVE"
    assert source_line.accumulator == "AC1"
    assert source_line.index_register == "INDEX"
    assert source_line.memory_address == "MEM"
    assert source_line.device_id is None
    assert source_line.is_indirect is True
    assert source_line.labels == ["LABEL1", "LABEL2", "LABEL3"]
    assert source_line.comment == "Some Words"


@pytest.mark.integration_test
def test_source_line_with_io_instruction(assembler):
    text = "LABEL1:LABEL2: LABEL3:    DATAO TTY,MEM(INDEX)  ;  Some Words"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_instruction is True
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is True
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator == "DATAO"
    assert source_line.accumulator is None
    assert source_line.device_id == "TTY"
    assert source_line.index_register == "INDEX"
    assert source_line.memory_address == "MEM"
    assert source_line.is_indirect is False
    assert source_line.labels == ["LABEL1", "LABEL2", "LABEL3"]
    assert source_line.comment == "Some Words"


@pytest.mark.integration_test
def test_source_line_with_assignment(assembler):
    text = "        A= 100  ;  Some Words"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assignment is True
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol == "A"
    assert source_line.assignment_value == "100"
    assert source_line.operator is None
    assert source_line.accumulator is None
    assert source_line.device_id is None
    assert source_line.index_register is None
    assert source_line.memory_address is None
    assert source_line.is_indirect is False
    assert source_line.labels == []
    assert source_line.comment == "Some Words"


@pytest.mark.integration_test
def test_source_line_with_empty_string(assembler):
    text = ""
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is True
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assignment is False
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator is None
    assert source_line.accumulator is None
    assert source_line.device_id is None
    assert source_line.index_register is None
    assert source_line.memory_address is None
    assert source_line.is_indirect is False
    assert source_line.labels == []
    assert source_line.comment is None


@pytest.mark.integration_test
def test_source_line_with_only_comment(assembler):
    text = "   ;  comment text"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is True
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assignment is False
    assert source_line.is_assemblable is False
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator is None
    assert source_line.accumulator is None
    assert source_line.device_id is None
    assert source_line.index_register is None
    assert source_line.memory_address is None
    assert source_line.is_indirect is False
    assert source_line.labels == []
    assert source_line.comment == "comment text"


@pytest.mark.integration_test
def test_source_line_with_halt(assembler):
    text = "FIN:  HALT 100"
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_instruction is True
    assert source_line.is_primary_instruction is True
    assert source_line.is_io_instruction is False
    assert source_line.is_assignment is False
    assert source_line.is_assemblable is True
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator == "HALT"
    assert source_line.accumulator is None
    assert source_line.device_id is None
    assert source_line.index_register is None
    assert source_line.memory_address == "100"
    assert source_line.is_indirect is False
    assert source_line.labels == ["FIN"]
    assert source_line.comment is None


@pytest.mark.integration_test
def test_source_line_with_value(assembler):
    text = "   7000   "
    source_line = SourceLine(assembler=assembler, source_line_number=1, text=text)
    source_line.read_text()
    assert source_line.is_empty is False
    assert source_line.is_instruction is False
    assert source_line.is_primary_instruction is False
    assert source_line.is_io_instruction is False
    assert source_line.is_assignment is False
    assert source_line.is_value is True
    assert source_line.is_assemblable is True
    assert source_line.assignment_symbol is None
    assert source_line.assignment_value is None
    assert source_line.operator is None
    assert source_line.accumulator is None
    assert source_line.device_id is None
    assert source_line.index_register is None
    assert source_line.memory_address is None
    assert source_line.value == "7000"
    assert source_line.is_indirect is False
    assert source_line.labels == []
    assert source_line.comment is None
