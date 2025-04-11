"""The main PDP10Assembler class."""

import sys

from .exceptions import AssemblyError
from .passes import FirstPassAssembler, SecondPassAssembler
from .pseudo_operators import PseudoOperators
from .source_line import SourceLine
from .symbol_table import SymbolTable


class PDP10Assembler:
    """DEC PDP-10 Assembler."""

    def __init__(self, text):
        """
        DEC PDP-10 Assembler.

        Args:
            text(str): The source code to assemble.
        """
        self.symbol_table = SymbolTable()
        self.pseudo_operators = PseudoOperators(self)
        self.text = text
        self.program = {}
        self.source_line_number = 0
        self.first_pass = FirstPassAssembler(assembler=self)
        self.second_pass = SecondPassAssembler(assembler=self)
        self.current_pass = self.first_pass

    def parse_text(self, text):
        """Return a list of SourceLine instances for each line of source."""
        source_lines = []
        for source_line_number, line_text in enumerate(text.splitlines(), 1):
            source_line = SourceLine(
                assembler=self, source_line_number=source_line_number, text=line_text
            )
            source_line.read_text()
            source_lines.append(source_line)
        return source_lines

    def assemble(self):
        """Assemble the source program."""
        self.run_text_parse()
        self.run_first_pass_assembly()
        self.current_pass = self.second_pass
        self.run_second_pass_assembly()

    def run_text_parse(self):
        """Run first pass assembly."""
        try:
            self.source_lines = self.parse_text(self.text)
        except AssemblyError as e:
            print(
                f"Error in parsing source line {self.first_pass.source_line_number}",
                file=sys.stderr,
            )
            print(self.first_pass.current_line, file=sys.stderr)
            print(str(e), file=sys.stderr)
            sys.exit(1)

    def run_first_pass_assembly(self):
        """Run first pass assembly."""
        try:
            self.first_pass.run()
        except AssemblyError as e:
            print(
                f"Error in first pass on line {self.first_pass.source_line_number}",
                file=sys.stderr,
            )
            print(self.first_pass.current_line, file=sys.stderr)
            print(str(e), file=sys.stderr)
            sys.exit(1)

    def run_second_pass_assembly(self):
        """Run second pass assembly."""
        try:
            self.second_pass.run()
        except AssemblyError as e:
            print(
                f"Error in second pass on line {self.second_pass.source_line_number}",
                file=sys.stderr,
            )
            print(self.second_pass.current_line, file=sys.stderr)
            print(str(e), file=sys.stderr)
            sys.exit(1)
