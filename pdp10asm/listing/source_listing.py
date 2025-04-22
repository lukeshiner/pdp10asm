"""The SourceListing class."""

from .base_listing import BaseListing


class SourceListing(BaseListing):
    """Create program listings in source code format."""

    labels_width = 10
    binary_value_width = 16

    def listing_text(self):
        """Return the program listing as a string."""
        header = self._header()
        source_lines = self._source_lines()
        return f"{header}\n{source_lines}"

    def _source_line(self, source_line):
        line = [
            self._format_source_line_number(source_line.source_line_number),
            self._format_labels(source_line.labels),
            self._format_instruction_text(source_line.instruction_text),
            self._format_memory_address(source_line.assembled_line.memory_location),
            self._format_binary_value(source_line.assembled_line.binary_value),
            self._format_comment(source_line.comment),
        ]
        return "".join(line)

    def _header(self):
        header = []
        underline = []
        for width, text in (
            (self.source_line_number_width, ""),
            (self.labels_width, "LABELS"),
            (self.instruction_width, "INSTRUCTION"),
            (self.memory_location_width, "ADDRESS"),
            (self.binary_value_width, "VALUE"),
            (25, "COMMENT"),
        ):
            header.append(f"{{:<{width}}}".format(text))
            underline.append(f"{{:_<{width}}}".format(""))
        return f"{''.join(header)}\n{''.join(underline)}"

    def _source_lines(self):
        lines = []
        for source_line in self.program.source_lines:
            lines.append(self._source_line(source_line))
        return "\n".join(lines)
