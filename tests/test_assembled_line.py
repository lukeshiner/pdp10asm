from unittest import mock

import pytest

from pdp10asm.program import AssembledLine


@pytest.fixture
def source_line():
    return mock.Mock()


@pytest.fixture
def memory_location():
    return 256


@pytest.fixture
def binary_value():
    return 0o202000100000


@pytest.fixture
def assembled_line(source_line, memory_location, binary_value):
    return AssembledLine(
        source_line=source_line,
        memory_location=memory_location,
        binary_value=binary_value,
    )


def test_assembled_line_has_source_line(assembled_line, source_line):
    assert assembled_line.source_line == source_line


def test_assembled_line_has_memory_location(assembled_line, memory_location):
    assert assembled_line.memory_location == memory_location


def test_assembled_line_has_binary_value(assembled_line, binary_value):
    assert assembled_line.binary_value == binary_value


def test_assembled_line_sets_source_line_assembled_line_property(
    assembled_line, source_line
):
    assert source_line.assembled_line == assembled_line
