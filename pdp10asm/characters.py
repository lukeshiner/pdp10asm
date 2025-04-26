"""Character handling for pdp10asm."""

from pdp10asm.constants import Constants
from pdp10asm.exceptions import AssemblyError


class Character:
    """Class for holding character information."""

    def __init__(self, name, character=None, ascii=None):
        """Create a character."""
        self.name = name
        self.character = character or name
        self.ascii = ascii or ord(self.character)
        self.sixbit = self.ascii - 0o40
        if self.sixbit < 0 or self.sixbit > 0o77:
            self.sixbit = None


class Characters:
    """Class for managing text characters."""

    characters = [
        Character("space", character=" "),
        Character("!"),
        Character('"'),
        Character("#"),
        Character("$"),
        Character("%"),
        Character("&"),
        Character("'"),
        Character("("),
        Character(")"),
        Character("*"),
        Character("+"),
        Character(","),
        Character("-"),
        Character("."),
        Character("/"),
        Character("0"),
        Character("1"),
        Character("2"),
        Character("3"),
        Character("4"),
        Character("5"),
        Character("6"),
        Character("7"),
        Character("8"),
        Character("9"),
        Character(":"),
        Character(";"),
        Character("<"),
        Character("="),
        Character(">"),
        Character("?"),
        Character("@"),
        Character("A"),
        Character("B"),
        Character("C"),
        Character("D"),
        Character("E"),
        Character("F"),
        Character("G"),
        Character("H"),
        Character("I"),
        Character("J"),
        Character("K"),
        Character("L"),
        Character("M"),
        Character("N"),
        Character("O"),
        Character("P"),
        Character("Q"),
        Character("R"),
        Character("S"),
        Character("T"),
        Character("U"),
        Character("V"),
        Character("W"),
        Character("X"),
        Character("Y"),
        Character("Z"),
        Character("["),
        Character("\\"),
        Character("]"),
        Character("^"),
        Character("_"),
        Character("`"),
        Character("a"),
        Character("b"),
        Character("c"),
        Character("d"),
        Character("e"),
        Character("f"),
        Character("g"),
        Character("h"),
        Character("i"),
        Character("j"),
        Character("k"),
        Character("l"),
        Character("m"),
        Character("n"),
        Character("o"),
        Character("p"),
        Character("q"),
        Character("r"),
        Character("s"),
        Character("t"),
        Character("u"),
        Character("v"),
        Character("w"),
        Character("x"),
        Character("y"),
        Character("z"),
        Character("{"),
        Character("|"),
        Character("}"),
        Character("~"),
        Character("delete", character="\x7f"),
        Character("\t"),
        Character("\n"),
        Character("vertical_tab", character="\x0b"),
        Character("form_feed", character="\x0c"),
        Character("\r"),
    ]

    @classmethod
    def by_name(cls, name):
        """Return a character by name."""
        for character in cls.characters:
            if character.name == name:
                return character
        raise ValueError(f"No character {name!r}.")

    @classmethod
    def by_character(cls, char, sixbit=False):
        """Return a character by name."""
        for character in cls.characters:
            if character.character == char:
                if sixbit is True and character.sixbit is None:
                    raise ValueError(f"{char!r} is not a valid sixbit character.")
                return character
        raise ValueError(f"No character {char!r}.")

    @classmethod
    def text_word_value(cls, text):
        """Return the value of a text word."""
        delimiter = text[0]
        if text[-1] == delimiter:
            stripped_text = text[1:-1]
            if delimiter == Constants.SEVEN_BIT_DELIMIETER:
                return cls.seven_bit_text_word_value(stripped_text)
            elif delimiter == Constants.SIX_BIT_DELIMITER:
                return cls.six_bit_text_word_value(stripped_text)
        raise AssemblyError(f"Invalid word string {text!r}.")

    @classmethod
    def get_ascii(cls, character):
        """Return the ascii value of a character."""
        try:
            return cls.by_character(character).ascii
        except ValueError as e:
            raise AssemblyError(f"Invalid character {character!r}.").with_traceback(
                e.__traceback__
            ) from None

    @classmethod
    def get_sixbit(cls, character):
        """Return the ascii value of a character."""
        try:
            return cls.by_character(character, sixbit=True).sixbit
        except ValueError as e:
            raise AssemblyError(
                f"Invalid sixbit character {character!r}."
            ).with_traceback(e.__traceback__) from None

    @classmethod
    def seven_bit_text_word_value(cls, text):
        """Return the value of a 7 bit text word."""
        if len(text) > 5:
            raise AssemblyError(f"{text!r} is too long for a 7-bit word.")
        word = 0
        for character in text:
            binary = cls.get_ascii(character)
            word = (word << 7) | binary
        return word

    @classmethod
    def six_bit_text_word_value(cls, text):
        """Return the value of a 6 bit text word."""
        if len(text) > 6:
            raise AssemblyError(f"{text!r} is too long for a 6-bit word.")
        word = 0
        for character in text:
            binary = cls.get_sixbit(character)
            word = (word << 6) | binary
        return word

    @classmethod
    def seven_bit_words(cls, text):
        """Return a string as 7-bit ascii in 36 bit words."""
        words = []
        word = 0
        shift = 36
        for character in text:
            shift -= 7
            binary = cls.get_ascii(character)
            word |= binary << shift
            if shift == 1:
                words.append(word)
                word = 0
                shift = 36
        if word != 0:
            words.append(word)
        return words

    @classmethod
    def six_bit_words(cls, text):
        """Return a string as 7-bit ascii in 36 bit words."""
        words = []
        word = 0
        shift = 36
        for character in text:
            shift -= 6
            binary = cls.get_sixbit(character)
            word |= binary << shift
            if shift == 0:
                words.append(word)
                word = 0
                shift = 36
        if word != 0:
            words.append(word)
        return words
