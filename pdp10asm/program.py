"""Classes for handling an assembled program."""

from pdp10asm.listing import BinaryListing

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
            listing_class = BinaryListing
        return listing_class(self, radix=radix).listing_text()
