"""PDP 10 Assembler constant values."""


class Constants:
    """Class for storing constant values."""

    COMMENT = ";"
    LABEL = ":"
    INDIRECT = "@"
    AC_SEPERATOR = ","
    RADIX_INDICATOR = "^"
    DECIMAL_INDICATOR = "^D"
    OCTAL_INDICATOR = "^O"
    BINARY_INDICATOR = "^B"
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
        MULTIPLY_OPERATOR,
        INTEGER_DIVIDE_OPERATOR,
        AND_OPERATOR,
        OR_OPERATOR,
        ADDITION_OPERATOR,
        SUBTRACTION_OPERATOR,
    ]
    PROGRAM_COUNTER_OPERAND = "."
