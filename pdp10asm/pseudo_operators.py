"""Assembler instructions for the PDP-10 Assembler."""


class PseudoOperators:
    """Class for handling assembler instructions."""

    def __init__(self, assembler):
        """Handle assembler instructions."""
        self.assembler = assembler
        self.instructions = {
            "LOC": self.loc,
            "END": self.end,
        }

    def is_pseudo_operator(self, word):
        """Return True if word in a pseudo operator."""
        return word.upper() in self.instructions

    def process_instruction(self, instruction_word, values):
        """Execute an assembler instruction."""
        instruction_method = self.instructions[instruction_word.upper()]
        instruction_method(values)

    def loc(self, values):
        """Change program counter."""
        self.assembler.current_pass.program_counter = values[0]

    def end(self, values):
        """Finish assembly."""
        self.assembler.current_pass.done = True
