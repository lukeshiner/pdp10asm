"""Classes for creating program listings."""

from pdp10asm.exceptions import ListingError


class BaseListing:
    """Class for creating assembly listings."""

    source_line_number_digits = 5
    source_line_number_width = 8

    symbol_name_width = 10
    symbol_value_width = 16
    symbol_line_number_width = 22

    labels_width = 14
    instruction_width = 20
    memory_location_width = 10
    binary_value_width = 14

    def __init__(self, program, radix=8):
        """Class for creating assembly listings."""
        self.program = program
        self.radix = radix

    def _format_symbol_name(self, symbol):
        text = f"{symbol.name}:"
        return f"{{:<{self.symbol_name_width}}}".format(text)

    def _format_symbol_value(self, symbol):
        text = self._format_36(symbol.value)
        return f"{{:<{self.symbol_value_width}}}".format(text)

    def _format_symbol_line_number(self, symbol):
        text = f"DEFINED ON: {symbol.source_line}"
        return f"{{:<{self.symbol_line_number_width}}}".format(text)

    def _format_labels(self, labels):
        if len(labels) == 0:
            return " " * self.labels_width
        else:
            lines = []
            for label in labels:
                lines.append(f"{{:<{self.labels_width}}}".format(label + ":"))
        return "\n".join(lines)

    def _format_instruction_text(self, instruction_text):
        if instruction_text is None:
            text = ""
        else:
            text = instruction_text
        return f"{{:<{self.instruction_width}}}".format(text)

    def _format_memory_address(self, memory_location):
        if memory_location is None:
            text = ""
        else:
            text = self._format_12(memory_location)
        return f"{{:<{self.memory_location_width}}}".format(text)

    def _format_binary_value(self, binary_value):
        if binary_value is None:
            text = ""
        else:
            text = self._format_36(binary_value)
        return f"{{:<{self.binary_value_width}}}".format(text)

    def _format_source_line_number(self, source_line_number):
        text = "{:d}".format(source_line_number)
        return f"{{:<{self.source_line_number_width}}}".format(
            f"{{:>{self.source_line_number_digits}}}".format(text)
        )

    def _format_comment(self, comment):
        if comment is None:
            return ""
        return comment

    def _format_36(self, value):
        if self.radix == 8:
            string = "{:012o}".format(value)
            return f"{string[:6]} {string[6:]}"
        elif self.radix == 2:
            return "{:036_b}".format(value)
        elif self.radix == 16:
            return "{:09x}".format(value).upper()
        elif self.radix == 10:
            return str(value)
        else:
            raise ListingError(f"Unsupported radix {self.radix}.")

    def _format_12(self, value):
        if self.radix == 8:
            return "{:06o}".format(value)
        elif self.radix == 2:
            return "{:018_b}".format(value)
        elif self.radix == 16:
            return "{:05x}".format(value).upper()
        elif self.radix == 10:
            return str(value)
        else:
            raise ListingError(f"Unsupported radix {self.radix}.")
