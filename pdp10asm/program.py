"""Classes for handling an assembled program."""

from .exceptions import AssemblyError


class AssembledLine:
    """Class for assembled lines of code."""

    def __init__(self, source_line, memory_location, binary_value):
        """Class for assembled lines of code."""
        self.source_line = source_line
        source_line.assembled_line = self
        self.memory_location = memory_location
        self.binary_value = binary_value


class Program:
    """Class for assembled programs."""

    def __init__(self):
        """Class for assembled programs."""
        self.assembled_lines = []
        self.by_source_line = {}
        self.by_memory_location = {}
        self.symbols = {}

    def add_line(self, source_line, memory_location, binary_value):
        """Add a line to the program."""
        if memory_location in self.by_memory_location:
            previous_source_line = self.by_memory_location[
                memory_location
            ].source_line.source_line_number
            raise AssemblyError(
                (
                    f"Memory location {memory_location:012o} already written to by "
                    f"source line {previous_source_line}."
                )
            )
        assembled_line = AssembledLine(
            source_line=source_line,
            memory_location=memory_location,
            binary_value=binary_value,
        )
        self.assembled_lines.append(source_line)
        self.by_source_line[assembled_line.source_line.source_line_number] = (
            assembled_line
        )
        self.by_memory_location[memory_location] = assembled_line
        return assembled_line

    def listing_text(self, listing_class=None, radix=8):
        """Return a program listing as a string."""
        if listing_class is None:
            listing_class = Listing
        return listing_class(self, radix=radix).listing_text()


class Listing:
    """Class for creating assembly listings."""

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

    def listing_text(self):
        """Return the program listing as a string."""
        symbols_text = self.symbols_listing_text()
        program_text = self.program_listing_text()
        return "\n\n".join((symbols_text, program_text))

    def symbols_listing_text(self):
        """Return the symbols listing text."""
        lines = []
        lines.append("SYMBOLS:")
        for symbol in self.program.symbols:
            lines.append(self._symbol_line(symbol))
        return "\n".join(lines)

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

    def _symbol_line(self, symbol):
        line = [
            self._format_symbol_name(symbol),
            self._format_symbol_value(symbol),
            self._format_symbol_line_number(symbol),
        ]
        return "".join(line)

    def _program_line(self, assembled_line):
        line = [
            self._format_labels(assembled_line),
            self._format_instruction_text(assembled_line),
            self._format_memory_address(assembled_line),
            self._format_binary_value(assembled_line),
        ]
        return "".join(line)

    def _format_symbol_name(self, symbol):
        text = f"{symbol.name}:"
        return f"{{:<{self.symbol_name_width}}}".format(text)

    def _format_symbol_value(self, symbol):
        text = self._format_36(symbol.value)
        return f"{{:<{self.symbol_value_width}}}".format(text)

    def _format_symbol_line_number(self, symbol):
        text = f"DEFINED ON: {symbol.source_line}"
        return f"{{:<{self.symbol_line_number_width}}}".format(text)

    def _format_labels(self, assembled_line):
        if len(assembled_line.source_line.labels) == 0:
            return " " * self.labels_width
        else:
            lines = []
            for label in assembled_line.source_line.labels:
                lines.append(f"{{:<{self.labels_width}}}".format(label + ":"))
        return "\n".join(lines)

    def _format_instruction_text(self, assembled_line):
        if assembled_line.source_line.instruction_text is None:
            text = ""
        else:
            text = assembled_line.source_line.instruction_text
        return f"{{:<{self.instruction_width}}}".format(text)

    def _format_memory_address(self, assembled_line):
        text = self._format_12(assembled_line.memory_location)
        return f"{{:<{self.memory_location_width}}}".format(text)

    def _format_binary_value(self, assembled_line):
        text = self._format_36(assembled_line.binary_value)
        return f"{{:<{self.binary_value_width}}}".format(text)

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
            raise AssemblyError(f"Unsupported radix {self.radix}.")

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
            raise AssemblyError(f"Unsupported radix {self.radix}.")
