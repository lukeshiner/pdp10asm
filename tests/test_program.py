from unittest import mock

import pytest

from pdp10asm.exceptions import AssemblyError
from pdp10asm.program import AssembledLine, Program


@pytest.fixture
def source_line():
    return mock.Mock(source_line_number=12)


@pytest.fixture
def memory_location():
    return 256


@pytest.fixture
def binary_value():
    return 0o202000100000


def test_program_as_assembled_lines():
    assert Program().assembled_lines == []


def test_program_has_source_lines():
    assert Program().source_lines == []


def test_program_has_by_memory_location():
    assert Program().by_memory_location == {}


def test_program_has_symbols():
    assert Program().symbols == {}


def test_add_line_returns_assembled_line(source_line, memory_location, binary_value):
    returned_value = Program().add_line(
        source_line=source_line,
        memory_location=memory_location,
        binary_value=binary_value,
    )
    assert isinstance(returned_value, AssembledLine)


def test_add_line_adds_assembled_line_to_by_memory_location(
    source_line, memory_location, binary_value
):
    program = Program()
    assembled_line = program.add_line(
        source_line=source_line,
        memory_location=memory_location,
        binary_value=binary_value,
    )
    assert program.by_memory_location[memory_location] == assembled_line


def test_add_line_raises_if_memory_location_already_exists(
    source_line, memory_location, binary_value
):
    program = Program()
    program.add_line(
        source_line=mock.Mock(source_line_number=5),
        memory_location=memory_location,
        binary_value=binary_value,
    )
    with pytest.raises(AssemblyError) as exc_info:
        program.add_line(
            source_line=source_line, memory_location=memory_location, binary_value=0
        )
    assert (
        str(exc_info.value)
        == "Memory location 000000000400 already written to by source line 5."
    )


def test_listing_text_returns_listing():
    program = Program()
    listing_class = mock.Mock()
    returned_value = program.listing_text(listing_class=listing_class, radix=16)
    assert returned_value == listing_class.return_value.listing_text.return_value
    listing_class.assert_called_once_with(program, radix=16)
    listing_class.return_value.listing_text.assert_called_once_with()


@mock.patch("pdp10asm.program.BinaryListing")
def test_listng_text_uses_defaults(mock_listing):
    program = Program()
    returned_value = program.listing_text()
    assert returned_value == mock_listing.return_value.listing_text.return_value
    mock_listing.assert_called_once_with(program, radix=8)
    mock_listing.return_value.listing_text.assert_called_once_with()
