from unittest import mock

import pytest

from pdp10asm.characters import Characters
from pdp10asm.exceptions import AssemblyError


@pytest.mark.parametrize(
    "name,character,ascii,sixbit",
    (
        ("space", " ", 0o040, 0),
        ("!", "!", 0o041, 0o01),
        ('"', '"', 0o042, 0o02),
        ("#", "#", 0o043, 0o03),
        ("$", "$", 0o044, 0o04),
        ("%", "%", 0o045, 0o05),
        ("&", "&", 0o046, 0o06),
        ("'", "'", 0o047, 0o07),
        ("(", "(", 0o050, 0o10),
        (")", ")", 0o051, 0o11),
        ("*", "*", 0o052, 0o12),
        ("+", "+", 0o053, 0o13),
        (",", ",", 0o054, 0o14),
        ("-", "-", 0o055, 0o15),
        (".", ".", 0o056, 0o16),
        ("/", "/", 0o057, 0o17),
        ("0", "0", 0o060, 0o20),
        ("1", "1", 0o061, 0o21),
        ("2", "2", 0o062, 0o22),
        ("3", "3", 0o063, 0o23),
        ("4", "4", 0o064, 0o24),
        ("5", "5", 0o065, 0o25),
        ("6", "6", 0o066, 0o26),
        ("7", "7", 0o067, 0o27),
        ("8", "8", 0o070, 0o30),
        ("9", "9", 0o071, 0o31),
        (":", ":", 0o072, 0o32),
        (";", ";", 0o073, 0o33),
        ("<", "<", 0o074, 0o34),
        ("=", "=", 0o075, 0o35),
        (">", ">", 0o076, 0o36),
        ("?", "?", 0o077, 0o37),
        ("@", "@", 0o100, 0o40),
        ("A", "A", 0o101, 0o41),
        ("B", "B", 0o102, 0o42),
        ("C", "C", 0o103, 0o43),
        ("D", "D", 0o104, 0o44),
        ("E", "E", 0o105, 0o45),
        ("F", "F", 0o106, 0o46),
        ("G", "G", 0o107, 0o47),
        ("H", "H", 0o110, 0o50),
        ("I", "I", 0o111, 0o51),
        ("J", "J", 0o112, 0o52),
        ("K", "K", 0o113, 0o53),
        ("L", "L", 0o114, 0o54),
        ("M", "M", 0o115, 0o55),
        ("N", "N", 0o116, 0o56),
        ("O", "O", 0o117, 0o57),
        ("P", "P", 0o120, 0o60),
        ("Q", "Q", 0o121, 0o61),
        ("R", "R", 0o122, 0o62),
        ("S", "S", 0o123, 0o63),
        ("T", "T", 0o124, 0o64),
        ("U", "U", 0o125, 0o65),
        ("V", "V", 0o126, 0o66),
        ("W", "W", 0o127, 0o67),
        ("X", "X", 0o130, 0o70),
        ("Y", "Y", 0o131, 0o71),
        ("Z", "Z", 0o132, 0o72),
        ("[", "[", 0o133, 0o73),
        ("\\", "\\", 0o134, 0o74),
        ("]", "]", 0o135, 0o75),
        ("^", "^", 0o136, 0o76),
        ("_", "_", 0o137, 0o77),
        ("`", "`", 0o140, None),
        ("a", "a", 0o141, None),
        ("b", "b", 0o142, None),
        ("c", "c", 0o143, None),
        ("d", "d", 0o144, None),
        ("e", "e", 0o145, None),
        ("f", "f", 0o146, None),
        ("g", "g", 0o147, None),
        ("h", "h", 0o150, None),
        ("i", "i", 0o151, None),
        ("j", "j", 0o152, None),
        ("k", "k", 0o153, None),
        ("l", "l", 0o154, None),
        ("m", "m", 0o155, None),
        ("n", "n", 0o156, None),
        ("o", "o", 0o157, None),
        ("p", "p", 0o160, None),
        ("q", "q", 0o161, None),
        ("r", "r", 0o162, None),
        ("s", "s", 0o163, None),
        ("t", "t", 0o164, None),
        ("u", "u", 0o165, None),
        ("v", "v", 0o166, None),
        ("w", "w", 0o167, None),
        ("x", "x", 0o170, None),
        ("y", "y", 0o171, None),
        ("z", "z", 0o172, None),
        ("{", "{", 0o173, None),
        ("|", "|", 0o174, None),
        ("}", "}", 0o175, None),
        ("~", "~", 0o176, None),
        ("delete", "\x7f", 0o177, None),
        ("\t", "\t", 0o011, None),
        ("\n", "\n", 0o012, None),
        ("vertical_tab", "\x0b", 0o013, None),
        ("form_feed", "\x0c", 0o014, None),
        ("\r", "\r", 0o015, None),
    ),
)
def test_characters(name, character, ascii, sixbit):
    char = Characters.by_name(name)
    assert char.name == name
    assert char.character == character
    assert char.ascii == ascii
    assert char.sixbit == sixbit


def test_by_name():
    assert Characters.by_name("space").character == " "


def test_by_name_with_invalid_character():
    with pytest.raises(ValueError) as e:
        Characters.by_name("invalid")
    assert str(e.value) == "No character 'invalid'."


def test_by_character():
    assert Characters.by_character(" ").name == "space"


def test_by_character_with_invalid_character():
    with pytest.raises(ValueError) as e:
        Characters.by_character("invalid")
    assert str(e.value) == "No character 'invalid'."


def test_by_character_with_sixbit():
    assert Characters.by_character(" ", sixbit=True).name == "space"


def test_by_character_with_invalid_sixbit():
    with pytest.raises(ValueError) as e:
        Characters.by_character("a", sixbit=True)
    assert str(e.value) == "'a' is not a valid sixbit character."


@mock.patch("pdp10asm.characters.Characters.seven_bit_text_word_value")
@mock.patch("pdp10asm.characters.Characters.six_bit_text_word_value")
def test_text_word_value_with_six_bit_word(
    mock_six_bit_text_word_value, mock_seven_bit_text_word_value
):
    return_value = Characters.text_word_value("'WORD'")
    mock_six_bit_text_word_value.assert_called_once_with("WORD")
    mock_seven_bit_text_word_value.assert_not_called()
    assert return_value == mock_six_bit_text_word_value.return_value


@mock.patch("pdp10asm.characters.Characters.seven_bit_text_word_value")
@mock.patch("pdp10asm.characters.Characters.six_bit_text_word_value")
def test_text_word_value_with_seven_bit_word(
    mock_six_bit_text_word_value, mock_seven_bit_text_word_value
):
    return_value = Characters.text_word_value('"WORD"')
    mock_seven_bit_text_word_value.assert_called_once_with("WORD")
    mock_six_bit_text_word_value.assert_not_called()
    assert return_value == mock_seven_bit_text_word_value.return_value


@pytest.mark.parametrize("text", ("WORD", '"WORD', "WORD'", 'WORD"', "'WORD", "WOW"))
def test_text_word_value_with_invalid_text(text):
    with pytest.raises(AssemblyError) as e:
        Characters.text_word_value(text)
    assert str(e.value) == f"Invalid word string {text!r}."


def test_get_ascii():
    assert Characters.get_ascii("a") == 0o141


def test_get_ascii_with_invalid_character():
    with pytest.raises(AssemblyError) as e:
        Characters.get_ascii("£")
    assert str(e.value) == "Invalid character '£'."


def test_get_sixbit():
    assert Characters.get_sixbit("A") == 0o41


def test_get_sixbit_with_invalid_character():
    with pytest.raises(AssemblyError) as e:
        Characters.get_sixbit("a")
    assert str(e.value) == "Invalid sixbit character 'a'."


@pytest.mark.parametrize(
    "text,expected",
    (
        ("AXE", 0b00000000000000100000110110001000101),
        ("Word", 0b00000001010111110111111100101100100),
        ("World", 0b10101111101111111001011011001100100),
    ),
)
def test_seven_bit_text_word_value(text, expected):
    assert Characters.seven_bit_text_word_value(text) == expected


def test_seven_bit_text_word_with_itoo_long_word():
    with pytest.raises(AssemblyError) as e:
        Characters.seven_bit_text_word_value("Worlds")
    assert str(e.value) == "'Worlds' is too long for a 7-bit word."


@pytest.mark.parametrize(
    "text,expected",
    (
        ("AXE", 0o000000417045),
        ("WORD", 0o000067576244),
        ("WORLD", 0o006757625444),
        ("WORLDS", 0o675762544463),
        ("TABLES", 0o644142544563),
    ),
)
def test_six_bit_text_word_value(text, expected):
    assert Characters.six_bit_text_word_value(text) == expected


def test_six_bit_text_word_with_too_long_word():
    with pytest.raises(AssemblyError) as e:
        Characters.six_bit_text_word_value("WORLDSA")
    assert str(e.value) == "'WORLDSA' is too long for a 6-bit word."


@pytest.mark.parametrize(
    "text,expected",
    (
        ("a", [0b110000100000000000000000000000000000]),
        ("A", [0b100000100000000000000000000000000000]),
        ("Hello", [0b100100011001011101100110110011011110]),
        (
            "Hello, World!",
            [
                0b100100011001011101100110110011011110,
                0b010110001000001010111110111111100100,
                0b110110011001000100001000000000000000,
            ],
        ),
    ),
)
def test_seven_bit_words(text, expected):
    assert Characters.seven_bit_words(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    (
        ("A", [0b100001000000000000000000000000000000]),
        ("HELLO,", [0b101000100101101100101100101111001100]),
        (
            "HELLO, WORLD!",
            [
                0b101000100101101100101100101111001100,
                0b000000110111101111110010101100100100,
                0b000001000000000000000000000000000000,
            ],
        ),
    ),
)
def test_six_bit_words(text, expected):
    assert Characters.six_bit_words(text) == expected
