"""The SourceLine class."""

from pdp10asm.pseudo_operators import PseudoOperators

from .constants import Constants
from .exceptions import AssemblyError
from .program import AssembledLine


class SourceLine:
    """Class for parsing source lines."""

    def __init__(self, assembler, source_line_number, text):
        """Class for parsing source lines."""
        self.assembler = assembler
        self.text = text
        self.source_line_number = source_line_number
        self.source_text = None
        self.memory_location_count = 0
        self.is_pseudo_operator = False
        self.is_assignment = False
        self.is_instruction = False
        self.is_primary_instruction = False
        self.is_io_instruction = False
        self.is_value = False
        self.is_text_word = False
        self.is_empty = True
        self.comment = None
        self.instruction_text = None
        self.labels = []
        self.operator = None
        self.assignment_symbol = None
        self.assignment_value = None
        self.operand = None
        self.accumulator = None
        self.index_register = None
        self.is_indirect = False
        self.memory_address = None
        self.device_id = None
        self.arguments = None
        self.value = None
        self.assembled_line = AssembledLine(self, None, None)

    def read_text(self):
        """Parse self.text."""
        text = self.text
        text = self._read_comment(text)
        text = self._read_labels(text)
        text = self._read_assignment(text)
        if self.is_assignment is True:
            return
        text = self._read_operator(text)
        if self.operator is None:
            return
        self._parse_instruction_type(text)
        try:
            self._parse_arguments(text)
        except Exception as e:
            raise AssemblyError(f"Unable to parse argument {text!r}.").with_traceback(
                e.__traceback__
            ) from e
        if self.is_pseudo_operator:
            operator = PseudoOperators.get_pseudo_op(self.operator)
            operator.source_line_process(self)

    @staticmethod
    def parse_address(text):
        """
        Return a parsed address operand.

        Returns:
            accumulator (str): The accumulator part of the address or None.
            index_register (str): The Index Register part of the address or None.
            memory_address (str): The address part of the address.
            is_indirect (bool): True if the address is indirect, otherwise False.
        """
        accumulator = None
        index_register = None
        memory_address = "0"
        is_indirect = False
        if Constants.AC_SEPERATOR in text:
            accumulator, text = text.split(Constants.AC_SEPERATOR)
            accumulator = accumulator.strip()
            if len(accumulator) == 0:
                accumulator = None
            if Constants.OPEN_INDEX_REGISTER in text:
                text, index_register = text.split(Constants.OPEN_INDEX_REGISTER)
                index_register = index_register.replace(
                    Constants.CLOSE_INDEX_REGISTER, ""
                ).strip()
                index_register = index_register
            text = text.strip()
        if text and text[0] == Constants.INDIRECT:
            is_indirect = True
            text = text[1:]
        if len(text) > 0:
            memory_address = text
        return accumulator, index_register, memory_address, is_indirect

    def _read_comment(self, text):
        if Constants.COMMENT in text:
            text, comment = text.split(Constants.COMMENT, maxsplit=1)
            self.comment = comment.strip()
        text = text.strip()
        if len(text) > 0:
            self.is_empty = False
        return text

    def _read_labels(self, text):
        while Constants.LABEL in text:
            label, text = text.split(Constants.LABEL, maxsplit=1)
            label = label.strip()
            if not Constants.is_symbol(label):
                raise AssemblyError(f"Invalid label {label!r}.")
            self.labels.append(label.strip())
        text = text.strip()
        if len(text) > 0:
            self.instruction_text = text
        return text.strip()

    def _read_assignment(self, text):
        operator = Constants.ASSIGNMENT_OPERATOR
        if text and text.split()[0].count(operator) > 0:
            try:
                self.assignment_symbol, self.assignment_value = [
                    _.strip() for _ in text.split(operator) if _.strip()
                ]
            except ValueError as e:
                raise AssemblyError(f"Invalid assignment {text!r}.") from e
            else:
                self.is_assignment = True
                return ""
        return text

    def _read_operator(self, text):
        text = text.strip()
        if len(text) == 0:
            self.operator = None
            return ""
        if text[0] in Constants.TEXT_WORD_DELIMITERS:
            self.is_text_word = True
            self.is_value = True
            self.operator = text
            return ""
        try:
            operator, remainder = text.split(maxsplit=1)
        except ValueError:
            self.operator = text.strip()
            return ""
        else:
            self.operator = operator.strip()
        return remainder.strip()

    def _parse_instruction_type(self, text):
        symbol_table = self.assembler.symbol_table
        if self.operator is None:
            return
        elif PseudoOperators.is_pseudo_op(self.operator) is True:
            self.is_pseudo_operator = True
        elif symbol_table.is_primary_instruction_symbol(self.operator) is True:
            self.is_instruction = True
            self.is_primary_instruction = True
            self.memory_location_count = 1
        elif symbol_table.is_io_instruction_symbol(self.operator) is True:
            self.is_instruction = True
            self.is_io_instruction = True
            self.memory_location_count = 1
        elif len(text.strip()) == 0:
            self.is_value = True
            self.memory_location_count = 1
            self.value = self.operator
            self.operator = None
        else:
            raise AssemblyError(f"Unable to parse {self.operator!r}.")

    def _parse_arguments(self, text):
        if self.is_pseudo_operator:
            self.arguments = text
        elif self.is_primary_instruction:
            self._parse_primary_operand(text)
        elif self.is_io_instruction:
            self._parse_io_operand(text)
        elif self.is_value:
            self._parse_value(text)
        else:
            raise AssemblyError(f"Statement not understood {text!r}.")

    def _parse_value(self, text):
        return text

    def _parse_primary_operand(self, text):
        self.accumulator, self.index_register, self.memory_address, self.is_indirect = (
            self.parse_address(text)
        )

    def _parse_io_operand(self, text):
        self.device_id, self.index_register, self.memory_address, self.is_indirect = (
            self.parse_address(text)
        )
