"""Output classes."""

from textwrap import wrap


class BaseOutput:
    """Base class for binary output formats."""

    def __init__(self, program):
        """
        Base class for binary output formats.

        Args:
            program (pdp10asm.program.Program): The assembled program to output.
        """
        self.program = program

    def write_file(self, filepath, *args, **kwargs):
        """
        Write the program to a file.

        Args:
            filepath (string or pathlib.Path): The path of the file to write.
        """
        data = self.get_output(*args, **kwargs)
        self.to_tape(filepath, data)

    def program_data(self):
        """Return dict(int,int) of memory location and binary data representing the program."""
        return {
            memory_location: assembled_line.binary_value
            for memory_location, assembled_line in self.program.by_memory_location.items()
        }

    @staticmethod
    def ints_to_binary(data):
        """Return a list of ints as bytes formatted for PDP-10 8-hole paper tape."""
        binary = bytearray()
        for word in data:
            word_text = f"{word:012o}"
            for nibble in wrap(word_text, 2):
                nibble_byte = int(f"2{nibble}", 8)
                binary.append(nibble_byte)
        return binary

    def to_tape(self, filepath, data):
        """
        Write data to filepath as a PDP-10 8-hole paper tape.

        Args:
            filepath (string or pathlib.Path): Path to the output file.
            data (list(int)): The data to write as a list of integer values.
        """
        binary = self.ints_to_binary(data)
        with open(filepath, "wb") as f:
            f.write(binary)

    def start_data(self, *args, **kwargs):
        """Return data to prepend to the output as a list of ints."""
        return []

    def end_data(self, *args, **kwargs):
        """Return data to append to the output as a list of ints."""
        return []

    def get_data(self, *args, **kwargs):
        """Override this method to return the data to be output as a list of ints."""
        raise NotImplementedError()

    def get_output(self, *args, **kwargs):
        """Return the full output data as a list of ints."""
        data = self.start_data(*args, **kwargs)
        data.extend(self.get_data(*args, **kwargs))
        data.extend(self.end_data(*args, **kwargs))
        return data


class RimOutput(BaseOutput):
    """Output class for writing PDP-6 style RIM loader paper tapes."""

    RIM_LOADER = [
        0o777770000001,
        0o710600000060,
        0o710740000010,
        0o254000000003,
        0o710440000010,
        0o710740000010,
        0o254000000006,
        0,
        0o254000000003,
    ]

    def write_file(self, filepath, loader=True, entry=0, halt=True):
        """
        Write a RIM format paper tape file.

        Args:
            filepath (string or pathlib.Path): The path to write the file to.

        Kwargs:
            loader (bool): If True the RIM loader will be prepended.
            entry (int): The address to jump to or halt on after loading.
            halt (bool): If True a halt command will be added at the end of the output,
                otherwise a JRST (jump) instruction.
        """
        super().write_file(filepath, loader=loader, entry=entry, halt=halt)

    def start_data(self, *args, **kwargs):
        """Return data to prepend to the output as a list of ints."""
        if kwargs.get("loader") is True:
            return list(self.RIM_LOADER)
        else:
            return []

    def end_data(self, *args, **kwargs):
        """Return data to append to the output as a list of ints."""
        if kwargs.get("halt") is True:
            end_instruction = 0o254200000000
        else:
            end_instruction = 0o254000000000
        return [end_instruction | kwargs.get("entry", 0)]

    def get_data(self, *args, **kwargs):
        """Return the program as a list of ints."""
        data = []
        for memory_location, value in self.program_data().items():
            data.append(0o710440000000 | memory_location)
            data.append(value)
        return data
