"""The ExpressionParser class."""

from .constants import Constants
from .exceptions import AssemblyError
from .source_line import SourceLine


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

    def __init__(self, text, assembler):
        """
        Evaluate expression text.

        Args:
            text (str): The string to be evaluated.
            assembler (PDP10Assembler): A reference to the assembler.
        """
        self.text = text
        self.assembler = assembler
        self.value = self.parse(self.text)

    def as_literal(self):
        """Return expression value as an integer."""
        self.validate_value(self.value)
        return self.value

    def as_twos_complement(self):
        """Return expression value as an integer."""
        value = self.to_twos_complement(self.value)
        self.validate_value(value)
        return value

    def symbol_or_value(self, text):
        """If word is a vaild symbol return it's value otherwise return a parsed number."""
        if text == Constants.PROGRAM_COUNTER_OPERAND:
            return self.assembler.current_pass.program_counter
        if SourceLine.is_symbol(text):
            return self.assembler.symbol_table.get_symbol_value(text)
        return self.value_to_int(text)

    @staticmethod
    def value_to_int(value, radix=8):
        """Return a value as an integer."""
        return int(value, radix)

    @staticmethod
    def to_twos_complement(value):
        """Return a value as its two's complement equivalent."""
        if value >= 0:
            return value
        return 0o777777777777 & value

    @staticmethod
    def validate_value(value):
        """Raise AssemblyError if value is not a valid 36-bit integer."""
        if value < 0 or value > 0o777777777777:
            raise AssemblyError(f"{value} is not a 36-bit number.")

    @staticmethod
    def expression_lexer(string):
        """Return string as a list of values and operators."""
        tokens = []
        token = []
        for char in string:
            if len(token) == 0 and char == Constants.SUBTRACTION_OPERATOR:
                token.append(string[0])
                continue
            if char in Constants.OPERATORS:
                tokens.append("".join(token).strip())
                tokens.append(char)
                token = []
            else:
                token.append(char)
        tokens.append("".join(token).strip())
        return tokens

    def parse(self, text):
        """Return the parsed value of the expression text."""
        expression = self.expression_lexer(text)
        return self._parse_expression(expression)

    def _parse_expression(self, expression):
        if len(expression) == 1:
            return self.symbol_or_value(expression[0])
        for operator in reversed(Constants.OPERATORS):
            if operator in expression:
                left = expression[: expression.index(operator)]
                right = expression[expression.index(operator) + 1 :]
                method = self.operations[operator]
                return method(
                    self._parse_expression(left),
                    self._parse_expression(right),
                )
        raise AssemblyError("Value operator mismatch.")
