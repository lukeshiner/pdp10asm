"""The BinaryListing class."""

from .base_listing import BaseListing


class BinaryListing(BaseListing):
    """Create listings in memory address order."""

    symbol_name_width = 10
    symbol_value_width = 16
    symbol_line_number_width = 22

    labels_width = 14
    instruction_width = 20
    memory_location_width = 10
    binary_value_width = 14

    def listing_text(self):
        """Return the program listing as a string."""
        heading = self.heading_text()
        symbols_text = self.symbols_listing_text()
        program_text = self.program_listing_text()
        return "\n\n".join((heading, symbols_text, program_text))

    def program_listing_text(self):
        """Return the program listing text."""
        lines = self._program_header()
        for assembled_line in self.program.by_memory_location.values():
            lines.append(self._program_line(assembled_line))
        return "\n".join(lines)

    def _program_header(self):
        header = []
        underline = []
        for width, text in (
            (self.labels_width, "LABELS"),
            (self.instruction_width, "INSTRUCTION"),
            (self.memory_location_width, "ADDRESS"),
            (self.binary_value_width, "VALUE"),
        ):
            header.append(f"{{:<{width}}}".format(text))
            underline.append(f"{{:_<{width}}}".format(""))
        return ["".join(header), "".join(underline)]

    def _program_line(self, assembled_line):
        line = [
            self._format_labels(assembled_line.source_line.labels),
            self._format_instruction_text(assembled_line.source_line.instruction_text),
            self._format_memory_address(assembled_line.memory_location),
            self._format_binary_value(assembled_line.binary_value),
        ]
        return "".join(line)
