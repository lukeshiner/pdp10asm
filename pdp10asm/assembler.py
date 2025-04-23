"""The main PDP10Assembler class."""

from .exceptions import AssemblyError
from .passes import FirstPassAssembler, SecondPassAssembler
from .program import Program
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
        self.program = Program()
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
        self.program.symbols = self.symbol_table.user_symbols()
        self.current_pass = self.second_pass
        self.run_second_pass_assembly()
        return self.program

    def run_text_parse(self):
        """Run first pass assembly."""
        try:
            self.program.source_lines = self.parse_text(self.text)
        except AssemblyError as e:
            for line in self._create_error_message("source processing", e):
                e.add_note(line)
            raise e

    def run_first_pass_assembly(self):
        """Run first pass assembly."""
        try:
            self.first_pass.run()
        except AssemblyError as e:
            for line in self._create_error_message("first pass", e):
                e.add_note(line)
            raise e

    def run_second_pass_assembly(self):
        """Run second pass assembly."""
        try:
            self.second_pass.run()
        except AssemblyError as e:
            for line in self._create_error_message("second pass", e):
                e.add_note(line)
            raise e

    def _create_error_message(self, pass_name, exception):
        return [
            f"During {pass_name} on line {self.current_pass.source_line_number}:",
            f"{self.current_pass.current_line!r}",
            str(exception),
        ]
