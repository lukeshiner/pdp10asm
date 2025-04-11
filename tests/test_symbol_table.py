from unittest import mock

import pytest

from pdp10asm.exceptions import AssemblyError
from pdp10asm.symbol_table import SymbolTable, UserSymbol


@pytest.fixture
def symbol_table():
    return SymbolTable()


@pytest.fixture
def symbol():
    return "SYMBOL"


@pytest.fixture
def value():
    return 55


def test_symbol_table_has_symbols(symbol_table):
    assert isinstance(symbol_table.symbol_table, dict)


def test_add_user_symbol_to_symbols(symbol_table, symbol, value):
    symbol_table.add_user_symbol(symbol, value, source_line=1)
    assert isinstance(symbol_table.symbol_table[symbol], UserSymbol)
    assert symbol_table.symbol_table[symbol].name == symbol
    assert symbol_table.symbol_table[symbol].value == value
    assert symbol_table.symbol_table[symbol].source_line == 1


def test_delete_symbol(symbol_table, symbol, value):
    symbol_table.symbol_table[symbol] = value
    symbol_table.delete_symbol(symbol)
    assert symbol not in symbol_table.symbol_table


def test_get_symbol_value(symbol_table, symbol, value):
    symbol_table.symbol_table[symbol] = UserSymbol(
        name=symbol, value=value, source_line=1
    )
    assert symbol_table.get_symbol_value(symbol) == value


def test_get_symbol_value_with_no_symbol_set(symbol_table):
    with pytest.raises(AssemblyError) as exc_info:
        symbol_table.get_symbol_value("SYMBOL")
    assert str(exc_info.value) == "Symbol 'SYMBOL' is not defined."


@mock.patch("pdp10asm.symbol_table.SymbolList")
def test_load_system_symbols(mock_symbol_list, symbol_table):
    mock_symbols = [mock.Mock()] * 3
    mock_symbol_list.get_system_symbols.return_value = mock_symbols
    symbol_table.add_symbol = mock.Mock()
    symbol_table.load_system_symbols()
    mock_symbol_list.get_system_symbols.assert_called_once_with()
    symbol_table.add_symbol.assert_has_calls(
        (mock.call(_) for _ in mock_symbols), any_order=False
    )


def test_user_symbols(symbol_table, symbol, value):
    symbol_table.add_user_symbol(symbol, value, 1)
    return_value = symbol_table.user_symbols()
    assert isinstance(return_value, list)
    assert len(return_value) == 1
    assert return_value[0].name == symbol


@pytest.mark.parametrize(
    "value,expected",
    (
        ("MOVE", True),
        ("DATAO", False),
        ("TTY", False),
        ("FOO", False),
        ("BAR", False),
        ("HALT", True),
    ),
)
def test_is_primary_instruction_symbol(value, expected, symbol_table):
    symbol_table.add_user_symbol("FOO", 55, 1)
    assert symbol_table.is_primary_instruction_symbol(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("MOVE", False),
        ("DATAO", True),
        ("TTY", False),
        ("FOO", False),
        ("BAR", False),
    ),
)
def test_is_io_instruction_symbol(value, expected, symbol_table):
    symbol_table.add_user_symbol("FOO", 55, 1)
    assert symbol_table.is_io_instruction_symbol(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("MOVE", False),
        ("DATAO", False),
        ("TTY", True),
        ("FOO", False),
        ("BAR", False),
    ),
)
def test_is_device_code_symbol(value, expected, symbol_table):
    symbol_table.add_user_symbol("FOO", 55, 1)
    assert symbol_table.is_device_code_symbol(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("MOVE", False),
        ("DATAO", False),
        ("TTY", False),
        ("FOO", True),
        ("BAR", False),
    ),
)
def test_is_user_symbol(value, expected, symbol_table):
    symbol_table.add_user_symbol("FOO", 55, 1)
    assert symbol_table.is_user_symbol(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    (
        ("MOVE", True),
        ("DATAO", True),
        ("TTY", True),
        ("FOO", True),
        ("BAR", False),
    ),
)
def test_is_defined(value, expected, symbol_table):
    symbol_table.add_user_symbol("FOO", 55, 1)
    assert symbol_table.is_defined(value) == expected


def test_base_symbol_repr_method():
    symbol = UserSymbol("SYMBOL", 10, 10)
    assert repr(symbol) == "<UserSymbol: SYMBOL>"
