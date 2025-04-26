from unittest import mock

import pytest

from pdp10asm.assembler import PDP10Assembler
from pdp10asm.exceptions import AssemblyError
from pdp10asm.passes import FirstPassAssembler, SecondPassAssembler
from pdp10asm.program import AssembledLine, Program
from pdp10asm.symbol_table import SymbolTable, UserSymbol


@pytest.fixture
def text():
    return " some assembly \n text"


@pytest.fixture
def pdp10assembler(text):
    return PDP10Assembler(text)


@pytest.fixture
def mock_parse_text(pdp10assembler):
    pdp10assembler.parse_text = mock.Mock()
    return pdp10assembler.parse_text


@pytest.fixture
def mock_first_pass(pdp10assembler):
    pdp10assembler.first_pass = mock.Mock()
    return pdp10assembler.first_pass


@pytest.fixture
def mock_second_pass(pdp10assembler):
    pdp10assembler.second_pass = mock.Mock()
    return pdp10assembler.second_pass


@pytest.fixture
def mock_run_text_parse(pdp10assembler):
    pdp10assembler.run_text_parse = mock.Mock()
    return pdp10assembler.run_text_parse


@pytest.fixture
def mock_run_first_pass_assembly(pdp10assembler):
    pdp10assembler.run_first_pass_assembly = mock.Mock()
    return pdp10assembler.run_first_pass_assembly


@pytest.fixture
def mock_run_second_pass_assembly(pdp10assembler):
    pdp10assembler.run_second_pass_assembly = mock.Mock()
    return pdp10assembler.run_second_pass_assembly


def test_assembler_has_symbols(pdp10assembler):
    assert isinstance(pdp10assembler.symbol_table, SymbolTable)


def test_assembler_has_text(pdp10assembler, text):
    assert pdp10assembler.text == text


def test_assembler_has_program(pdp10assembler):
    assert isinstance(pdp10assembler.program, Program)


def test_has_first_pass_assembler(pdp10assembler):
    assert isinstance(pdp10assembler.first_pass, FirstPassAssembler)


def test_has_second_pass_assembler(pdp10assembler):
    assert isinstance(pdp10assembler.second_pass, SecondPassAssembler)


def test_assembler_has_radix(pdp10assembler):
    assert pdp10assembler.radix == 8


def test_assembler_has_curent_pass(pdp10assembler):
    assert pdp10assembler.current_pass == pdp10assembler.first_pass


def test_assemble_method_calls_text_parse(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.assemble()
    mock_run_text_parse.assert_called_once_with()


def test_assemble_method_runs_first_pass(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.assemble()
    mock_run_first_pass_assembly.assert_called_once_with()


def test_assemble_method_runs_second_pass(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.assemble()
    mock_run_second_pass_assembly.assert_called_once_with()


def test_assemble_method_updates_current_pass(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.assemble()
    assert pdp10assembler.current_pass == pdp10assembler.second_pass


def test_assemble_method_resets_radix(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.radix = 10
    pdp10assembler.assemble()
    assert pdp10assembler.radix == 8


def test_assemble_method_sets_program_symbols(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    pdp10assembler.symbol_table = mock.Mock()
    pdp10assembler.assemble()
    assert (
        pdp10assembler.program.symbols
        == pdp10assembler.symbol_table.user_symbols.return_value
    )


def test_assemble_method_returns_program(
    mock_run_text_parse,
    mock_run_first_pass_assembly,
    mock_run_second_pass_assembly,
    pdp10assembler,
):
    assert pdp10assembler.assemble() == pdp10assembler.program


def test_run_text_parse(mock_parse_text, pdp10assembler):
    pdp10assembler.run_text_parse()
    mock_parse_text.assert_called_once_with(pdp10assembler.text)


def test_run_text_parse_with_error(mock_parse_text, pdp10assembler):
    pdp10assembler.current_pass = mock_parse_text
    mock_parse_text.source_line_number = 12
    mock_parse_text.current_line = "TEXT WITH ERROR"
    mock_parse_text.side_effect = AssemblyError("error text")
    with pytest.raises(AssemblyError) as e:
        pdp10assembler.run_text_parse()
    mock_parse_text.assert_called_once_with(pdp10assembler.text)
    assert e.value.__notes__ == [
        "During source processing on line 12:",
        "'TEXT WITH ERROR'",
        "error text",
    ]


def test_run_first_pass_assembly(mock_first_pass, pdp10assembler):
    pdp10assembler.run_first_pass_assembly()
    mock_first_pass.run.assert_called_once_with()


def test_run_first_pass_assembly_with_error(mock_first_pass, pdp10assembler):
    pdp10assembler.current_pass = mock_first_pass
    mock_first_pass.source_line_number = 12
    mock_first_pass.current_line = "TEXT WITH ERROR"
    mock_first_pass.run.side_effect = AssemblyError("error text")
    with pytest.raises(AssemblyError) as e:
        pdp10assembler.run_first_pass_assembly()
    mock_first_pass.run.assert_called_once_with()
    assert e.value.__notes__ == [
        "During first pass on line 12:",
        "'TEXT WITH ERROR'",
        "error text",
    ]


def test_run_second_pass_assembly(mock_second_pass, pdp10assembler):
    pdp10assembler.run_second_pass_assembly()
    mock_second_pass.run.assert_called_once_with()


def test_run_second_pass_assembly_with_error(mock_second_pass, pdp10assembler):
    pdp10assembler.current_pass = mock_second_pass
    mock_second_pass.source_line_number = 12
    mock_second_pass.current_line = "TEXT WITH ERROR"
    mock_second_pass.run.side_effect = AssemblyError("error text")
    with pytest.raises(AssemblyError) as e:
        pdp10assembler.run_second_pass_assembly()
    mock_second_pass.run.assert_called_once_with()
    assert e.value.__notes__ == [
        "During second pass on line 12:",
        "'TEXT WITH ERROR'",
        "error text",
    ]


@mock.patch("pdp10asm.assembler.SourceLine")
def test_parse_text(mock_SourceLine, pdp10assembler):
    text = "1\n2\n3\n"
    return_value = pdp10assembler.parse_text(text)
    mock_SourceLine.assert_has_calls(
        (
            mock.call(assembler=pdp10assembler, source_line_number=1, text="1"),
            mock.call().read_text(),
            mock.call(assembler=pdp10assembler, source_line_number=2, text="2"),
            mock.call().read_text(),
            mock.call(assembler=pdp10assembler, source_line_number=3, text="3"),
            mock.call().read_text(),
        ),
        any_order=False,
    )
    assert return_value == [mock_SourceLine.return_value] * 3


# Integration Tests
@pytest.fixture
def test_symbol():
    def _test_symbol(symbol, symbol_name, value, source_line):
        assert isinstance(symbol, UserSymbol)
        assert symbol.name == symbol_name
        assert symbol.value == value
        assert symbol.source_line == source_line

    return _test_symbol


@pytest.fixture
def test_assembled_value():
    def _test_assembled_value(program, memory_location, binary_value):
        assert (
            memory_location in program.by_memory_location
        ), f"Memory Location {memory_location:06o} was not set."
        assert isinstance(program.by_memory_location[memory_location], AssembledLine)
        assembled_line = program.by_memory_location[memory_location]
        assert (
            assembled_line.memory_location == memory_location
        ), f"Assembled memory location {assembled_line.memory_location:012b} does not match acutal location {memory_location:06o}"
        assert (
            assembled_line.binary_value == binary_value
        ), f"Memory location {memory_location:06o}: {assembled_line.binary_value:012o} does not match {binary_value:012o}"

    return _test_assembled_value


@pytest.fixture
def assembly_test(test_symbol, test_assembled_value):
    def _assembly_test(text, symbols, program_values):
        assembler = PDP10Assembler(text)
        program = assembler.assemble()
        for i, symbol_tuple in enumerate(symbols):
            test_symbol(program.symbols[i], *symbol_tuple)
        for memory_location, binary_value in program_values.items():
            test_assembled_value(
                program=program,
                memory_location=memory_location,
                binary_value=binary_value,
            )

    return _assembly_test


@pytest.mark.integration_test
def test_assembly_of_hello_world(assembly_test, hello_world_text):
    symbols = [
        ("LOOP", 0o101, 9),
        ("PLOOP", 0o104, 12),
        ("FIN", 0o107, 15),
        ("POINT", 0o200, 18),
    ]
    program_values = {
        0o000100: 0o200040000200,
        0o000101: 0o134100000001,
        0o000102: 0o322100000107,
        0o000103: 0o712140000002,
        0o000104: 0o712300000020,
        0o000105: 0o324000000104,
        0o000106: 0o324000000101,
        0o000107: 0o254200000100,
        0o000200: 0o441100000201,
        0o000201: 0o110145154154,
        0o000202: 0o157054040127,
        0o000203: 0o157162154144,
        0o000204: 0o041015012000,
    }
    assembly_test(hello_world_text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_of_memory_to_paper_tape_raw(
    assembly_test, memory_to_paper_tape_raw_text
):
    symbols = [
        ("START", 0o770200, 10),
        ("STARTADD", 0, 12),
        ("NBYTES", 1, 13),
        ("POINT", 2, 14),
        ("CURADD", 3, 15),
        ("BLEFT", 4, 16),
        ("OUT", 5, 17),
        ("WORDL", 0o770204, 24),
        ("BYTEL", 0o770205, 25),
        ("NEWW", 0o770213, 31),
        ("FIN", 0o770215, 33),
    ]
    program_values = {
        0o770200: 0o710200000050,
        0o770201: 0o200140000001,
        0o770202: 0o505100440600,
        0o770203: 0o540100000000,
        0o770204: 0o201200000006,
        0o770205: 0o134240000002,
        0o770206: 0o710140000005,
        0o770207: 0o710340000010,
        0o770210: 0o254000770207,
        0o770211: 0o362200770213,
        0o770212: 0o254000770205,
        0o770213: 0o361140770215,
        0o770214: 0o254000770204,
        0o770215: 0o254200770200,
    }
    assembly_test(memory_to_paper_tape_raw_text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_dec_psedudo_op(assembly_test):
    text = "LOC 100\nDEC 10,20+5, 45,23534,-56\nLABEL:10\nEND"
    symbols = [
        ("LABEL", 0o105, 3),
    ]
    program_values = {
        0o100: 10,
        0o101: 25,
        0o102: 45,
        0o103: 23534,
        0o104: 68719476680,
        0o105: 0o10,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_oct_psedudo_op(assembly_test):
    text = """LOC 100
            OCT 4+4,25, 45,23534,-56
    LABEL:  10
            END
    """
    symbols = [
        ("LABEL", 0o105, 3),
    ]
    program_values = {
        0o100: 0o10,
        0o101: 0o25,
        0o102: 0o45,
        0o103: 0o23534,
        0o104: 68719476690,
        0o105: 0o10,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_bare_value(assembly_test):
    text = """LOC 100
            A=2
            B=5
    REX:    A+B
            END"""
    symbols = [
        ("A", 0o2, 2),
        ("B", 0o5, 3),
        ("REX", 0o100, 4),
    ]
    program_values = {
        0o100: 0o7,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_Z(assembly_test):
    text = """LOC 100
        Z
        Z 3,
        Z 3,2
        Z 3,@2
        Z 3,@2(1)
        END
    """
    symbols = []
    program_values = {
        0o100: 0,
        0o101: 0o000140000000,
        0o102: 0o000140000002,
        0o103: 0o000160000002,
        0o104: 0o000161000002,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_POINT(assembly_test):
    text = """LOC 100
        ADD=47777777
        POINT 36,ADD,36
        END
    """
    symbols = [("ADD", 0o47777777, 2)]
    program_values = {0o100: 0o444447777777}
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_IOWD(assembly_test):
    text = """LOC 100
        IOWD 6,^D256
        END
    """
    symbols = []
    program_values = {0o100: 0o777772000377}
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_7_bit_word(assembly_test):
    text = """LOC 100
        "AXE"
        END
    """
    symbols = []
    program_values = {0o100: 0b00000000000000100000110110001000101}
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_6_bit_word(assembly_test):
    text = """LOC 100
        'TABLES'
        END
    """
    symbols = []
    program_values = {0o100: 0b110100100001100010101100100101110011}
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_6_bit_word_with_space(assembly_test):
    text = """LOC 100
        'TAB ES'
        END
    """
    symbols = []
    program_values = {0o100: 0b110100100001100010000000100101110011}
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_ascii_pseudo_op(assembly_test):
    text = """LOC 100
        ASCII "Hello, World!"
        END
    """
    symbols = []
    program_values = {
        0o100: 0b100100011001011101100110110011011110,
        0o101: 0b010110001000001010111110111111100100,
        0o102: 0b110110011001000100001000000000000000,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_asciz_pseudo_op(assembly_test):
    text = """LOC 100
        ASCIZ "Hello, World!12"
        END
    """
    symbols = []
    program_values = {
        0o100: 0b100100011001011101100110110011011110,
        0o101: 0b010110001000001010111110111111100100,
        0o102: 0b110110011001000100001011000101100100,
        0o103: 0,
    }
    assembly_test(text, symbols, program_values)


@pytest.mark.integration_test
def test_assembly_with_sixbit_pseudo_op(assembly_test):
    text = """LOC 100
        SIXBIT "HELLO, WORLD!"
        END
    """
    symbols = []
    program_values = {
        0o100: 0b101000100101101100101100101111001100,
        0o101: 0b000000110111101111110010101100100100,
        0o102: 0b000001000000000000000000000000000000,
    }
    assembly_test(text, symbols, program_values)
