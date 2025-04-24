import pytest

from pdp10asm.constants import Constants


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
    assert Constants.is_symbol(word) is expected
