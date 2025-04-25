"""The ExpressionParser class."""

from .constants import Constants
from .exceptions import AssemblyError


class Operations:
    """Methods for performing operations."""

    @staticmethod
    def addition_operation(first_operand, second_operand):
        """Return the result of an addition operation."""
        return first_operand + second_operand

    @staticmethod
    def subtraction_operation(first_operand, second_operand):
        """Return the result of a subtraction operation."""
        return first_operand - second_operand

    @staticmethod
    def multiply_operation(first_operand, second_operand):
        """Return the result of a multiply operation."""
        return first_operand * second_operand

    @staticmethod
    def divide_operation(first_operand, second_operand):
        """Return the result of an integer divide operation."""
        return first_operand // second_operand

    @staticmethod
    def and_operation(first_operand, second_operand):
        """Return the result of a logical AND operation."""
        return first_operand & second_operand

    @staticmethod
    def or_operation(first_operand, second_operand):
        """Return the result of a logical OR operation."""
        return first_operand | second_operand


class ExpressionParser:
    """Methods for evaluating expressions."""

    operations = {
        Constants.AND_OPERATOR: Operations.and_operation,
        Constants.OR_OPERATOR: Operations.or_operation,
        Constants.MULTIPLY_OPERATOR: Operations.multiply_operation,
        Constants.INTEGER_DIVIDE_OPERATOR: Operations.divide_operation,
        Constants.ADDITION_OPERATOR: Operations.addition_operation,
        Constants.SUBTRACTION_OPERATOR: Operations.subtraction_operation,
    }

    def __init__(self, text, assembler, radix=None):
        """
        Evaluate expression text.

        Args:
            text (str): The string to be evaluated.
            assembler (PDP10Assembler): A reference to the assembler.
        """
        self.text = text
        self.radix = radix
        self.assembler = assembler
        self.value = self.parse(self.text)

    def as_literal(self):
        """Return expression value as an integer."""
        self.validate_word(self.value)
        return self.value

    def as_twos_complement(self):
        """Return expression value as an integer."""
        value = self.to_twos_complement(self.value)
        self.validate_word(value)
        return value

    def as_half_word(self, negative=False):
        """Return value as an 18-bit integer, if negative is True return two's complement."""
        value = self.value
        if negative is True:
            value = value * -1
        if value < 0:
            value = 0o777777 & value
        self.validate_half_word(value)
        return value

    def symbol_or_value(self, token):
        """If word is a vaild symbol return it's value otherwise return a parsed number."""
        if isinstance(token, int):
            return token
        if token == Constants.PROGRAM_COUNTER_OPERAND:
            return self.assembler.current_pass.program_counter
        if Constants.is_symbol(token):
            return self.assembler.symbol_table.get_symbol_value(token)
        return self.value_to_int(token)

    def value_to_int(self, value):
        """Return a value as an integer."""
        value, radix = self.handle_radix(value)
        value, magnitude = self.handle_magnitude(value)
        return int(value, radix) * magnitude

    def handle_radix(self, value):
        """Return the value with radix qualifier removed and the radix."""
        for indicator, radix in Constants.RADIX_QUALIFIERS.items():
            if indicator in value:
                return value.replace(indicator, "").strip(), radix
        return value, self.radix or self.assembler.radix

    def handle_magnitude(self, value):
        """Return value with magnitude removed and the magnitude value."""
        for suffix, magnitude in Constants.MAGNITUDE_SUFFIXES.items():
            if value.endswith(suffix):
                return value[: -len(suffix)].strip(), magnitude
        return value, 1

    @staticmethod
    def to_twos_complement(value):
        """Return a value as its two's complement equivalent."""
        if value >= 0:
            return value
        return 0o777777777777 & value

    @staticmethod
    def validate_word(value):
        """Raise AssemblyError if value is not a valid 36-bit integer."""
        if value < 0 or value > 0o777777777777:
            raise AssemblyError(f"{value} is not a 36-bit number.")

    @staticmethod
    def validate_half_word(value):
        """Raise AssemblyError if value is not a valid 36-bit integer."""
        if value < 0 or value > 0o777777:
            raise AssemblyError(f"{value} is not an 18-bit number.")

    @staticmethod
    def expression_lexer(string):
        """Return string as a list of values and operators."""
        string = string.strip()
        tokens = []
        while string is not None and len(string) > 0:
            if string[0] == "<":
                end_bracked_index = string.rfind(">")
                bracketed = string[1:end_bracked_index].strip()
                string = string[end_bracked_index + 1 :].strip()
                tokens.append(ExpressionParser.expression_lexer(bracketed))
            else:
                token, string = ExpressionParser.get_token(string)
                tokens.append(token)
        return tokens

    @staticmethod
    def get_token(string):
        """Return the first token in a string."""
        token = []
        split_characters = Constants.OPERATORS + ["<", ">", "."]
        for char in split_characters:
            if string[0].startswith(char):
                return char.strip(), string[len(char) :].strip()
        for i, char in enumerate(string):
            token.append(char)
            if i < len(string) - 1 and string[i + 1] in split_characters:
                return "".join(token).strip(), string[i + 1 :].strip()
        return "".join(token).strip(), None

    def parse(self, text):
        """Return the parsed value of the expression text."""
        expression = self.expression_lexer(text)
        return self._parse_expression(expression)

    def _parse_expression(self, expression):
        for i, token in enumerate(expression):
            if isinstance(token, list):
                expression[i] = self._parse_expression(token)
        if len(expression) == 1:
            return self.symbol_or_value(expression[0])
        for operator in reversed(Constants.OPERATORS):
            if operator in expression:
                operator_index = expression.index(operator)
                if operator == Constants.SUBTRACTION_OPERATOR:
                    if (
                        operator_index == 0
                        or expression[operator_index - 1] in Constants.OPERATORS
                    ):
                        value = expression.pop(operator_index + 1)
                        expression[operator_index] = 0 - self._parse_expression([value])
                        return self._parse_expression(expression)
                left = expression[:operator_index]
                right = expression[operator_index + 1 :]
                method = self.operations[operator]
                return method(
                    self._parse_expression(left),
                    self._parse_expression(right),
                )
        raise AssemblyError(f"Value operator mismatch {expression!r}.")
