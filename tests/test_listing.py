from unittest import mock

import pytest

from pdp10asm.assembler import PDP10Assembler
from pdp10asm.exceptions import ListingError
from pdp10asm.listing import BinaryListing


@pytest.fixture
def program():
    return mock.Mock()


@pytest.fixture
def listing(program):
    return BinaryListing(program=program)


def test_listing_takes_program(program):
    assert BinaryListing(program=program).program == program


def test_listing_takes_radix(program):
    assert BinaryListing(program=program, radix=16).radix == 16


def test_listing_radix_defaults_to_8(program):
    assert BinaryListing(program).radix == 8


def test_listing_text(listing):
    listing.symbols_listing_text = mock.Mock(return_value="symbols")
    listing.program_listing_text = mock.Mock(return_value="program")
    assert listing.listing_text() == "symbols\n\nprogram"


def test_symbols_listing_text(listing):
    listing.program.symbols = [mock.Mock()] * 3
    listing._symbol_line = mock.Mock(return_value="text")
    assert listing.symbols_listing_text() == "SYMBOLS:\ntext\ntext\ntext"
    listing._symbol_line.assert_has_calls(
        (mock.call(_) for _ in listing.program.symbols), any_order=False
    )


def test_program_listing_text(listing):
    assembled_lines = [mock.Mock()] * 3
    listing.program.by_memory_location.values.return_value = assembled_lines
    listing._program_line = mock.Mock(return_value="text")
    listing._program_header = mock.Mock(return_value=["header"])
    assert listing.program_listing_text() == "header\ntext\ntext\ntext"
    listing._program_line.assert_has_calls(
        (mock.call(_) for _ in assembled_lines), any_order=False
    )


def test_program_header(listing):
    returned_value = listing._program_header()
    assert returned_value == [
        "LABELS        INSTRUCTION         ADDRESS   VALUE         ",
        "__________________________________________________________",
    ]


def test_symbol_line(listing):
    symbol = mock.Mock()
    listing._format_symbol_name = mock.Mock(return_value="NAME")
    listing._format_symbol_value = mock.Mock(return_value="VALUE")
    listing._format_symbol_line_number = mock.Mock(return_value="LINE")
    assert listing._symbol_line(symbol) == "NAMEVALUELINE"
    listing._format_symbol_name.assert_called_once_with(symbol)
    listing._format_symbol_value.assert_called_once_with(symbol)
    listing._format_symbol_line_number.assert_called_once_with(symbol)


def test_program_line(listing):
    assembled_line = mock.Mock()
    listing._format_labels = mock.Mock(return_value="LABEL")
    listing._format_instruction_text = mock.Mock(return_value="INST")
    listing._format_memory_address = mock.Mock(return_value="LOC")
    listing._format_binary_value = mock.Mock(return_value="BIN")
    assert listing._program_line(assembled_line) == "LABELINSTLOCBIN"
    listing._format_labels.assert_called_once_with(assembled_line)
    listing._format_instruction_text.assert_called_once_with(assembled_line)
    listing._format_memory_address.assert_called_once_with(assembled_line)
    listing._format_binary_value.assert_called_once_with(assembled_line)


def test_format_symbol_name(listing):
    symbol = mock.Mock()
    symbol.name = "SYMBOL"
    assert listing._format_symbol_name(symbol) == "SYMBOL:   "


def test_format_symbol_value(listing):
    symbol = mock.Mock(value=255)
    assert listing._format_symbol_value(symbol) == "000000 000377   "


def test_format_symbol_line_number(listing):
    symbol = mock.Mock(source_line=12)
    assert listing._format_symbol_line_number(symbol) == "DEFINED ON: 12        "


@pytest.mark.parametrize(
    "labels,expected",
    (
        (["LABEL"], "LABEL:        "),
        ([], "              "),
        (
            ["LABEL1", "LABEL2", "LABEL3"],
            "LABEL1:       \nLABEL2:       \nLABEL3:       ",
        ),
    ),
)
def test_format_labels(labels, expected, listing):
    assembled_line = mock.Mock()
    assembled_line.source_line.labels = labels
    assert listing._format_labels(assembled_line) == expected


@pytest.mark.parametrize(
    "instruction_text,expected",
    (
        ("MOV 200", "MOV 200             "),
        (None, "                    "),
    ),
)
def test_format_instruction_text(instruction_text, expected, listing):
    assembled_line = mock.Mock()
    assembled_line.source_line.instruction_text = instruction_text
    assert listing._format_instruction_text(assembled_line) == expected


def test_format_memory_address(listing):
    assembled_line = mock.Mock(memory_location=255)
    assert listing._format_memory_address(assembled_line) == "000377    "


def test_format_binary_value(listing):
    assembled_line = mock.Mock(binary_value=255)
    assert listing._format_binary_value(assembled_line) == "000000 000377 "


@pytest.mark.parametrize(
    "value,radix,expected",
    (
        (0o123123123123, 8, "123123 123123"),
        (255, 8, "000000 000377"),
        (255, 10, "255"),
        (255, 16, "0000000FF"),
        (255, 2, "0_0000_0000_0000_0000_0000_1111_1111"),
    ),
)
def test_format_36(value, radix, expected, listing):
    listing.radix = radix
    assert listing._format_36(value) == expected


def test_format_36_raises_for_unsupported_radix(listing):
    listing.radix = 3
    with pytest.raises(ListingError) as exc_info:
        listing._format_36(255)
    assert str(exc_info.value) == "Unsupported radix 3."


@pytest.mark.parametrize(
    "value,radix,expected",
    (
        (0o123123, 8, "123123"),
        (255, 8, "000377"),
        (255, 10, "255"),
        (255, 16, "000FF"),
        (255, 2, "000_0000_1111_1111"),
    ),
)
def test_format_12(value, radix, expected, listing):
    listing.radix = radix
    assert listing._format_12(value) == expected


def test_format_12_raises_for_unsupported_radix(listing):
    listing.radix = 3
    with pytest.raises(ListingError) as exc_info:
        listing._format_12(255)
    assert str(exc_info.value) == "Unsupported radix 3."


@pytest.mark.integration_test
def test_hello_world_listing(hello_world_text, hello_world_listing_text):
    assembler = PDP10Assembler(hello_world_text)
    program = assembler.assemble()
    listing = BinaryListing(program=program)
    assert listing.listing_text() == hello_world_listing_text


@pytest.mark.integration_test
def test_memory_to_paper_tape_raw_listing(
    memory_to_paper_tape_raw_text, memory_to_paper_tape_raw_listing_text
):
    assembler = PDP10Assembler(memory_to_paper_tape_raw_text)
    program = assembler.assemble()
    listing = BinaryListing(program=program)
    assert listing.listing_text() == memory_to_paper_tape_raw_listing_text
