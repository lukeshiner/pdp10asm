from unittest import mock

import pytest

from pdp10asm.output import BaseOutput


@pytest.fixture
def program():
    return mock.Mock()


@pytest.fixture
def base_output(program):
    return BaseOutput(program=program)


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


def test_base_output_has_program(program):
    assert BaseOutput(program).program == program


def test_write_file(args, kwargs, base_output):
    base_output.get_output = mock.Mock()
    base_output.to_tape = mock.Mock()
    filepath = "path.rim"
    base_output.write_file(filepath, *args, **kwargs)
    base_output.get_output.assert_called_once_with(*args, **kwargs)
    base_output.to_tape.assert_called_once_with(
        filepath, base_output.get_output.return_value
    )


def test_program_data(memory_locations, base_output):
    assert base_output.program_data() == {100: 20, 200: 30, 250: 40}


def test_ints_to_binary(base_output):
    data = {100: 20, 200: 30, 250: 40}
    assert base_output.ints_to_binary(data) == bytearray(
        b"\x80\x80\x80\x80\x81\xa4\x80\x80\x80\x80\x83\x88\x80\x80\x80\x80\x83\xba"
    )


def test_to_tape(tmpdir, base_output):
    data = b"\x80\x80\x80\x80\x81\xa4\x80\x80\x80\x80\x83\x88\x80\x80\x80\x80\x83\xba"
    filepath = tmpdir.join("output.rim")
    base_output.ints_to_binary = mock.Mock(return_value=bytearray(data))
    base_output.to_tape(filepath, data)
    with open(filepath, "rb") as f:
        assert f.read() == data


def test_start_data(args, kwargs, base_output):
    assert base_output.start_data(*args, **kwargs) == []


def test_end_data(args, kwargs, base_output):
    assert base_output.end_data(*args, **kwargs) == []


def test_get_data(args, kwargs, base_output):
    with pytest.raises(NotImplementedError):
        base_output.get_data(*args, **kwargs)


def test_get_output(args, kwargs, base_output):
    base_output.start_data = mock.Mock(return_value=[1])
    base_output.get_data = mock.Mock(return_value=[2])
    base_output.end_data = mock.Mock(return_value=[3])
    returned_value = base_output.get_output(*args, **kwargs)
    base_output.start_data.assert_called_once_with(*args, **kwargs)
    base_output.get_data.assert_called_once_with(*args, **kwargs)
    base_output.end_data.assert_called_once_with(*args, **kwargs)
    assert returned_value == [1, 2, 3]
