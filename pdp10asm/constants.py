"""PDP 10 Assembler constant values."""


class Constants:
    """Class for storing constant values."""

    COMMENT = ";"
    LABEL = ":"
    INDIRECT = "@"
    AC_SEPERATOR = ","
    QUALIFIER_INDICATOR = "^"
    DECIMAL_QUALIFIER = "^D"
    OCTAL_QUALIFIER = "^O"
    BINARY_QUALIFIER = "^B"
    RADIX_QUALIFIERS = {
        DECIMAL_QUALIFIER: 10,
        OCTAL_QUALIFIER: 8,
        BINARY_QUALIFIER: 2,
    }
    MAGNITUDE_SUFFIXES = {
        "K": 1000,
        "M": 1000000,
        "G": 1000000000,
    }
    BINARY_SHIFT_INDICATOR = "B"
    SYMBOL_SPECIAL_CHARACTERS = ["%", "$", "."]
    OPEN_INDEX_REGISTER = "("
    CLOSE_INDEX_REGISTER = ")"
    INDIRECT_BIT = 0o20000000
    ASSIGNMENT_OPERATOR = "="
    ADDITION_OPERATOR = "+"
    SUBTRACTION_OPERATOR = "-"
    MULTIPLY_OPERATOR = "*"
    INTEGER_DIVIDE_OPERATOR = "/"
    AND_OPERATOR = "&"
    OR_OPERATOR = "|"
    OPERATORS = [
        INTEGER_DIVIDE_OPERATOR,
        MULTIPLY_OPERATOR,
        AND_OPERATOR,
        OR_OPERATOR,
        ADDITION_OPERATOR,
        SUBTRACTION_OPERATOR,
    ]
    PROGRAM_COUNTER_OPERAND = "."

    @staticmethod
    def is_symbol(word):
        """Return True if word is a symbol, otherwise False."""
        if word[0].isnumeric():
            return False
        for character in word:
            if (
                not character.isalnum()
                and character not in Constants.SYMBOL_SPECIAL_CHARACTERS
            ):
                return False
            if word == ".":
                return False
        return True
