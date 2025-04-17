"""Classes for first and second pass assembly."""

from .constants import Constants
from .exceptions import AssemblyError
from .expressions import ExpressionParser


class BaseAssemblerPass:
    """Base class for assembler passes."""

    def __init__(self, assembler):
        """
        Base class for assembler passes.

        Kwargs:
            assembler (PDP10Assembler): The parent assembler.
            text_lines (list(str)): List of lines of source code.
        """
        self.assembler = assembler
        self.symbol_table = assembler.symbol_table
        self.pseudo_operators = assembler.pseudo_operators
        self.program_counter = 0
        self.source_line_number = 0
        self.current_line = ""
        self.current_line_comment = ""
        self.done = False

    def run(self):
        """Run the assembly pass."""
        for source_line in self.assembler.source_lines:
            if self.done is True:
                return
            if source_line.is_empty:
                continue
            self.process_line(source_line)
            if source_line.is_assemblable:
                self.program_counter += 1

    def handle_pseudo_operator(self, source_line):
        """Execute an assembler instruction."""
        values = [self.literal_value(value) for value in source_line.arguments.split()]
        self.pseudo_operators.process_instruction(
            instruction_word=source_line.operator, values=values
        )

    def process_line(self, words):
        """Process a line of assembly."""
        raise NotImplementedError()

    def symbol_value(self, symbol):
        """Return the value of a symbol from the symbol table."""
        return self.symbol_table.get_symbol_value(symbol)

    def validate_value(self, value):
        """Raise AssemblyError if value is not a valid 36-bit integer."""
        if value < 0 or value > 0o777777777777:
            raise AssemblyError(f"{value} is not a 36-bit number.")

    def literal_value(self, text):
        """Parse text and return as a literal value."""
        return ExpressionParser(text, self.assembler).as_literal()

    def twos_complement_value(self, text):
        """Parse text and return as a two's complement value."""
        return ExpressionParser(text, self.assembler).as_twos_complement()


class FirstPassAssembler(BaseAssemblerPass):
    """Class for performing first pass assembly."""

    def process_line(self, source_line):
        """Process a line of source."""
        if source_line.is_pseudo_operator:
            self.handle_pseudo_operator(source_line)
        elif source_line.is_assignment:
            self.handle_assignments(source_line)
        else:
            self.handle_labels(source_line)

    def handle_labels(self, source_line):
        """Add labels to the symbol table and return words without them."""
        for label in source_line.labels:
            self.add_label(label, source_line.source_line_number)

    def handle_assignments(self, source_line):
        """Add symbols for an assignment."""
        if not source_line.is_assignment:
            return
        value = self.twos_complement_value(source_line.assignment_value)
        self.symbol_table.add_user_symbol(
            symbol=source_line.assignment_symbol,
            value=value,
            source_line=source_line.source_line_number,
        )

    def add_label(self, label_text, source_line_number):
        """Add a label to the symbol table."""
        self.symbol_table.add_user_symbol(
            symbol=label_text,
            value=self.program_counter,
            source_line=source_line_number,
        )


class SecondPassAssembler(BaseAssemblerPass):
    """Class for performing first pass assembly."""

    def process_line(self, source_line):
        """Process a line of source."""
        if source_line.is_assignment is True:
            return
        elif source_line.is_pseudo_operator is True:
            self.handle_pseudo_operator(source_line)
            return
        if source_line.is_assemblable is True:
            instruction_word = self.assemble_line(source_line)
            self.assembler.program[self.program_counter] = instruction_word

    def assemble_line(self, source_line):
        """Return the binary word represented by line."""
        if source_line.is_value is True:
            return self.twos_complement_value(source_line.value)
        operator_binary = self.symbol_value(source_line.operator)
        if source_line.is_primary_instruction is True:
            operand = self.primary_operand_value(source_line)
        elif source_line.is_io_instruction is True:
            operand = self.io_operand_value(source_line)
        else:
            raise AssemblyError(f"Unable to parse line {source_line.text!r}")
        return operator_binary | operand

    def primary_operand_value(self, source_line):
        """Return the operand part of an instruction word."""
        operand = 0
        operand |= self.accumulator_value(source_line.accumulator)
        operand |= self.index_register_value(source_line.index_register)
        operand |= self.address_value(source_line.memory_address)
        if source_line.is_indirect is True:
            operand |= Constants.INDIRECT_BIT
        return operand

    def io_operand_value(self, source_line):
        """Return the operand part of an IO instruction word."""
        operand = 0
        operand |= self.device_id_value(source_line.device_id)
        operand |= self.index_register_value(source_line.index_register)
        operand |= self.address_value(source_line.memory_address)
        if source_line.is_indirect is True:
            operand |= Constants.INDIRECT_BIT
        return operand

    def accumulator_value(self, accumulator):
        """Return the accumulator address part of an opreand word.."""
        if accumulator is None:
            return 0
        accumulator_value = self.literal_value(accumulator)
        self.validate_accumulator_value(accumulator_value)
        return accumulator_value << 23

    def validate_accumulator_value(self, value):
        """Raise and exception if value is not a valid accumulator id."""
        if value < 0 or value > 0b1111:
            raise AssemblyError(f"{value} is not a valid accumulator.")

    def address_value(self, memory_address):
        """Return the address part of an operand word."""
        memory_address_value = self.literal_value(memory_address)
        self.validate_address(memory_address_value)
        return memory_address_value

    def validate_address(self, value):
        """Raise AssemblyError if address is not valid."""
        if value < 0 or value > 0o777777:
            raise AssemblyError(f"{value} is not a valid memory address.")

    def index_register_value(self, index_register):
        """Return the index regsiter part of an operand word."""
        if index_register is None:
            return 0
        index_register_value = self.literal_value(index_register)
        self.validate_index_register_value(index_register_value)
        return index_register_value << 18

    def validate_index_register_value(self, value):
        """Raise AssemblyError if index register is not valid."""
        if value < 0 or value > 0b1111:
            raise AssemblyError(f"{value} is not a valid index register.")

    def device_id_value(self, device_id):
        """Return the device ID part of an IO opreand word."""
        if device_id is None:
            return 0
        device_id_value = self.literal_value(device_id)
        self.validate_device_id(device_id_value)
        return device_id_value << 24

    def validate_device_id(self, value):
        """Raise AssemblyError if value is not a valid device ID."""
        if value < 0 or value > 0o774 or value % 4 != 0:
            raise AssemblyError(f"{value} is not a valid device id.")
