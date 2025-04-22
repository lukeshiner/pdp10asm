from unittest import mock

import pytest

from pdp10asm import PDP10Assembler
from pdp10asm.output import RimOutput


@pytest.fixture
def program():
    return mock.Mock()


@pytest.fixture
def rim_output(program):
    return RimOutput(program=program)


@pytest.fixture
def args():
    return [mock.Mock()]


@pytest.fixture
def kwargs():
    return {"a": mock.Mock(), "b": mock.Mock()}


@pytest.fixture
def memory_locations(program):
    program.by_memory_location = {
        100: mock.Mock(binary_value=20),
        200: mock.Mock(binary_value=30),
        250: mock.Mock(binary_value=40),
    }


def test_rim_output_has_program(program):
    assert RimOutput(program).program == program


@mock.patch("pdp10asm.output.BaseOutput.write_file")
def test_write_file(mock_super_write_file, rim_output):
    filepath = "path.rim"
    rim_output.write_file(filepath, loader=False, entry=0o100, halt=False)
    mock_super_write_file.assert_called_once_with(
        filepath, loader=False, entry=0o100, halt=False
    )


def test_program_data(memory_locations, rim_output):
    assert rim_output.program_data() == {100: 20, 200: 30, 250: 40}


def test_ints_to_binary(rim_output):
    data = {100: 20, 200: 30, 250: 40}
    assert rim_output.ints_to_binary(data) == bytearray(
        b"\x80\x80\x80\x80\x81\xa4\x80\x80\x80\x80\x83\x88\x80\x80\x80\x80\x83\xba"
    )


def test_to_tape(tmpdir, rim_output):
    data = b"\x80\x80\x80\x80\x81\xa4\x80\x80\x80\x80\x83\x88\x80\x80\x80\x80\x83\xba"
    filepath = tmpdir.join("output.rim")
    rim_output.ints_to_binary = mock.Mock(return_value=bytearray(data))
    rim_output.to_tape(filepath, data)
    with open(filepath, "rb") as f:
        assert f.read() == data


def test_start_data_without_loader(rim_output):
    assert rim_output.start_data(loader=False) == []


def test_start_data_with_loader(rim_output):
    return_value = rim_output.start_data(loader=True)
    assert return_value == RimOutput.RIM_LOADER
    assert return_value is not RimOutput.RIM_LOADER


@pytest.mark.parametrize(
    "halt,entry,expected",
    (
        (True, 0o100, 0o254200000100),
        (False, 0o200, 0o254000000200),
    ),
)
def test_end_data(halt, entry, expected, rim_output):
    assert rim_output.end_data(entry=entry, halt=halt) == [expected]


def test_get_data(args, kwargs, rim_output):
    rim_output.program_data = mock.Mock(
        return_value={0o100: 0o20, 0o200: 0o30, 0o250: 0o40}
    )
    assert rim_output.get_data(*args, **kwargs) == [
        0o710440000100,
        0o20,
        0o710440000200,
        0o30,
        0o710440000250,
        0o40,
    ]


def test_get_output(args, kwargs, rim_output):
    rim_output.start_data = mock.Mock(return_value=[1])
    rim_output.get_data = mock.Mock(return_value=[2])
    rim_output.end_data = mock.Mock(return_value=[3])
    returned_value = rim_output.get_output(*args, **kwargs)
    rim_output.start_data.assert_called_once_with(*args, **kwargs)
    rim_output.get_data.assert_called_once_with(*args, **kwargs)
    rim_output.end_data.assert_called_once_with(*args, **kwargs)
    assert returned_value == [1, 2, 3]


@pytest.fixture
def test_rim_output(tmpdir):
    def _test_rim_output(source, expected, halt, entry, loader):
        program = PDP10Assembler(source).assemble()
        output = RimOutput(program)
        path = tmpdir.join("out.rim")
        output.write_file(path, loader=loader, entry=entry, halt=halt)
        with open(path, "rb") as f:
            assert f.read() == expected

    return _test_rim_output


@pytest.mark.integration_test
def test_ouput_hello_world(test_rim_output, hello_world_text, hello_world_rim_data):
    test_rim_output(
        hello_world_text, hello_world_rim_data, loader=True, entry=0o100, halt=False
    )


@pytest.mark.integration_test
def test_ouput_memory_to_paper_tape_raw(
    test_rim_output, memory_to_paper_tape_raw_text, memory_to_paper_tape_raw_rim_data
):
    test_rim_output(
        memory_to_paper_tape_raw_text,
        memory_to_paper_tape_raw_rim_data,
        loader=True,
        entry=0o770200,
        halt=True,
    )
