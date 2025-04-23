import os
from unittest import mock

import pytest
from click.testing import CliRunner

from pdp10asm import exceptions
from pdp10asm.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def filesystem(runner):
    with runner.isolated_filesystem() as dir:
        yield dir


@pytest.fixture
def source_file(filesystem, hello_world_text):
    source_path = "source.asm"
    with open(source_path, "w") as f:
        f.write(hello_world_text)
    return source_path


@pytest.fixture
def out_file(filesystem):
    return "out.rim"


@pytest.fixture
def listing_file(filesystem):
    return "listing.txt"


def test_cli(source_file, runner):
    result = runner.invoke(cli, [source_file])
    assert result.exit_code == 0
    assert "Assembling source.asm" in result.output


def test_cli_creates_output_file(filesystem, out_file, source_file, runner):
    result = runner.invoke(cli, [source_file, "-o", out_file])
    assert result.exit_code == 0
    with open(out_file, "rb") as f:
        assert f.read()
    assert f"Saved binary to {filesystem}/{out_file}" in result.output


def test_cli_does_not_create_output_file_if_output_file_not_passed(source_file, runner):
    result = runner.invoke(cli, [source_file])
    assert os.listdir() == [source_file]
    assert result.exit_code == 0


def test_cli_does_not_allow_invalid_formats(source_file, runner):
    result = runner.invoke(cli, [source_file, "-f", "INVALID"])
    assert result.exit_code == 2
    assert "Error: Invalid value for '-f' / '--format': 'INVALID'" in result.output


def test_cli_does_not_allow_invalid_listing_formats(source_file, runner):
    result = runner.invoke(cli, [source_file, "-lf", "INVALID"])
    assert result.exit_code == 2
    assert (
        "Error: Invalid value for '-lf' / '--listing-format': 'INVALID'"
        in result.output
    )


def test_cli_does_not_allow_invalid_listing_radix(source_file, runner):
    result = runner.invoke(cli, [source_file, "-r", "INVALID"])
    assert result.exit_code == 2
    assert "Error: Invalid value for '-r' / '--radix': 'INVALID'" in result.output


@pytest.fixture
def mock_output_format():
    m = mock.Mock()
    with mock.patch("pdp10asm.cli.OUTPUT_FORMATS", {"RIM": m}):
        yield m


def test_passes_handles_loader_option(
    mock_output_format, filesystem, source_file, out_file, runner
):
    result = runner.invoke(cli, [source_file, "-o", out_file, "--loader"])
    mock_output_format.return_value.write_file.assert_called_once_with(
        f"{filesystem}/{out_file}", loader=True, halt=True
    )
    assert result.exit_code == 0


def test_passes_handles_no_loader_option(
    mock_output_format, filesystem, source_file, out_file, runner
):
    result = runner.invoke(cli, [source_file, "-o", out_file, "--no-loader"])
    mock_output_format.return_value.write_file.assert_called_once_with(
        f"{filesystem}/{out_file}", loader=False, halt=True
    )
    assert result.exit_code == 0


def test_passes_handles_halt_option(
    mock_output_format, filesystem, source_file, out_file, runner
):
    result = runner.invoke(cli, [source_file, "-o", out_file, "--halt"])
    mock_output_format.return_value.write_file.assert_called_once_with(
        f"{filesystem}/{out_file}", loader=True, halt=True
    )
    assert result.exit_code == 0


def test_passes_handles_jump_option(
    mock_output_format, filesystem, source_file, out_file, runner
):
    result = runner.invoke(cli, [source_file, "-o", out_file, "--jump"])
    mock_output_format.return_value.write_file.assert_called_once_with(
        f"{filesystem}/{out_file}", loader=True, halt=False
    )
    assert result.exit_code == 0


def test_listing_file(filesystem, source_file, listing_file, runner):
    result = runner.invoke(cli, [source_file, "-l", listing_file])
    assert result.exit_code == 0
    assert f"Saved listing to {filesystem}/{listing_file}" in result.output
    with open(listing_file, "r") as f:
        assert f.read()


@mock.patch("pdp10asm.cli.click.echo_via_pager")
def test_pager_option(mock_echo_via_pager, source_file, runner):
    result = runner.invoke(cli, [source_file, "-p"])
    mock_echo_via_pager.assert_called_once()
    assert result.exit_code == 0


def test_no_listing_option(source_file, runner):
    result = runner.invoke(cli, [source_file, "-nl"])
    assert result.exit_code == 0
    assert result.output == "Assembling source.asm.\n\nAssembly successful\n\n"


@mock.patch("pdp10asm.cli.PDP10Assembler")
def test_error_creating_assembler(mock_assembler, source_file, runner):
    mock_assembler.side_effect = exceptions.AssemblyError()
    mock_assembler.side_effect.add_note("error text")
    result = runner.invoke(cli, [source_file])
    assert result.exit_code == 1
    assert "error text" in result.output


@mock.patch("pdp10asm.cli.PDP10Assembler")
def test_error_running_assembler(mock_assembler, source_file, runner):
    mock_assembler.return_value.assemble.side_effect = exceptions.AssemblyError()
    mock_assembler.return_value.assemble.side_effect.add_note("error text")
    result = runner.invoke(cli, [source_file])
    assert result.exit_code == 1
    assert "error text" in result.output


@mock.patch("pdp10asm.cli.PDP10Assembler")
def test_error_creating_listing(mock_assembler, source_file, runner):
    mock_assembler.return_value.assemble.return_value.listing_text.side_effect = (
        exceptions.ListingError("error text")
    )
    result = runner.invoke(cli, [source_file])
    assert result.exit_code == 1
    assert "error text" in result.output


@pytest.mark.integration_test
def test_second_pass_error(filesystem, runner, second_pass_error_text):
    source_path = "source.asm"
    with open(source_path, "w") as f:
        f.write(second_pass_error_text)
    result = runner.invoke(cli, [source_path])
    assert result.exit_code == 1
    assert result.output == (
        "Assembling source.asm.\n\n"
        "Error: During second pass on line 1:\n'DATAO 777,0'\n"
        "777 is not a valid device id.\n"
    )
