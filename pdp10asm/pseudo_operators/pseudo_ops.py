"""Pseudo operators."""

from pdp10asm.expressions import ExpressionParser


class PseudoOp:
    """Base class for pseudo operators."""

    name = ""
    first_pass = False
    second_pass = False

    @staticmethod
    def process(assembler, source_line):
        """Perform the psedudo operation."""
        raise NotImplementedError


class Loc(PseudoOp):
    """The LOC pseudo op."""

    name = "LOC"
    first_pass = True
    second_pass = True

    @staticmethod
    def process(assembler, source_line):
        """Set the program counter to a new value."""
        assembler.current_pass.program_counter = ExpressionParser(
            source_line.arguments, assembler
        ).as_literal()


class End(PseudoOp):
    """The END pseudo op."""

    name = "END"
    first_pass = True
    second_pass = True

    @staticmethod
    def process(assembler, source_line):
        """End the current pass."""
        assembler.current_pass.done = True


class Title(PseudoOp):
    """The TITLE pseudo op."""

    name = "TITLE"
    first_pass = True
    second_pass = False

    @staticmethod
    def process(assembler, source_line):
        """Set the program's title."""
        assembler.program.title = source_line.arguments


class Subtitle(PseudoOp):
    """The SUBTTLE pseudo op."""

    name = "SUBTTLE"
    first_pass = True
    second_pass = False

    @staticmethod
    def process(assembler, source_line):
        """Set the program's subtitle."""
        assembler.program.subtitle = source_line.arguments
