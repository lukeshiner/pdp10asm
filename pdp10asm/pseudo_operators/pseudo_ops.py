"""Pseudo operators."""

from pdp10asm.exceptions import AssemblyError
from pdp10asm.expressions import ExpressionParser


class PseudoOp:
    """Base class for pseudo operators."""

    name = ""
    first_pass = False
    second_pass = False

    @classmethod
    def process(cls, assembler, source_line):
        """Perform the psedudo operation."""
        raise NotImplementedError

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = 0


class Loc(PseudoOp):
    """The LOC pseudo op."""

    name = "LOC"
    first_pass = True
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Set the program counter to a new value."""
        assembler.current_pass.program_counter = ExpressionParser(
            source_line.arguments, assembler
        ).as_literal()


class End(PseudoOp):
    """The END pseudo op."""

    name = "END"
    first_pass = True
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """End the current pass."""
        assembler.current_pass.done = True


class Title(PseudoOp):
    """The TITLE pseudo op."""

    name = "TITLE"
    first_pass = True
    second_pass = False

    @classmethod
    def process(cls, assembler, source_line):
        """Set the program's title."""
        assembler.program.title = source_line.arguments


class Subtitle(PseudoOp):
    """The SUBTTLE pseudo op."""

    name = "SUBTTLE"
    first_pass = True
    second_pass = False

    @classmethod
    def process(cls, assembler, source_line):
        """Set the program's subtitle."""
        assembler.program.subtitle = source_line.arguments


class Radix(PseudoOp):
    """The RADIX pseudo op."""

    name = "RADIX"
    first_pass = True
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Change the prevailing radix."""
        invalid = False
        try:
            radix = int(source_line.arguments)
        except ValueError:
            invalid = True
        if invalid is True or radix < 2 or radix > 10:
            raise AssemblyError(f"Invalid Radix {source_line.argurments!r}")
        assembler.radix = radix


class Exp(PseudoOp):
    """The Exp pseudo op."""

    name = "EXP"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add literals."""
        values = [
            ExpressionParser(value, assembler, radix=None).as_twos_complement()
            for value in source_line.arguments.split(",")
        ]
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=values
        )

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = len(source_line.arguments.split(","))


class Dec(PseudoOp):
    """The DEC pseudo op."""

    name = "DEC"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add decimal literals."""
        values = [
            ExpressionParser(value, assembler, radix=10).as_twos_complement()
            for value in source_line.arguments.split(",")
        ]
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=values
        )

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = len(source_line.arguments.split(","))


class Oct(PseudoOp):
    """The OCT pseudo op."""

    name = "OCT"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add decimal literals."""
        values = [
            ExpressionParser(value, assembler, radix=8).as_twos_complement()
            for value in source_line.arguments.split(",")
        ]
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=values
        )

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = len(source_line.arguments.split(","))


class Byte(PseudoOp):
    """The BYTE pseudo op."""

    name = "BYTE"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add bytes of n length."""
        length, arguments = cls.parse(source_line.arguments)
        values = [
            ExpressionParser(argument, assembler).as_twos_complement()
            for argument in arguments
        ]
        binary_values = cls.get_binary_values(length, values)
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=binary_values
        )

    @classmethod
    def get_binary_values(cls, length, values):
        """Return the binary words represented by the BYTE instruciton."""
        words = []
        binary_format = f"{{:0{length}b}}"
        word = ""
        for value in values:
            if len(word) + length > 36:
                words.append(f"{word:0<36}")
                word = ""
            binary_text = binary_format.format(value)[-length:]
            word += binary_text
        words.append(f"{word:0<36}")
        return [int(word, 2) for word in words]

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        length, values = cls.parse(source_line.arguments)
        source_line.memory_location_count = cls.word_count(length, len(values))

    @classmethod
    def word_count(cls, length, values):
        """Return the number of words represented by the BYTE instruction."""
        count = (values * length) // 36
        if (values * length) % 36 > 1:
            count += 1
        return count

    @classmethod
    def parse(cls, text):
        """Return byte length and values strings."""
        if text[0] == "(" and ")" in text:
            length_text, values = text[1:].split(")")
            values = [_.strip() for _ in values.split(",")]
            try:
                length = int(length_text)
            except ValueError:
                pass
            else:
                if length >= 1 and length <= 36:
                    return length, values
        raise AssemblyError(f"Invalid argument to BYTE {text!r}.")


class Point(PseudoOp):
    """The POINT pseudo op."""

    name = "POINT"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add bytes of n length."""
        byte_size_text, address_text, position_text = cls.parse(source_line.arguments)
        byte_size = cls.convert_byte_size(byte_size_text)
        position = cls.convert_position(position_text)
        address = assembler.symbol_table.get_symbol_value(address_text)
        value = cls.create_point(
            byte_size=byte_size, address=address, position=position
        )
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=[value]
        )

    @classmethod
    def create_point(cls, byte_size, address, position):
        """Return the binary value of a POINT statement as an int."""
        return (position << 30) | (byte_size << 24) | address

    @classmethod
    def convert_byte_size(cls, byte_size_text):
        """Return the value of the byte size argument."""
        try:
            byte_size = int(byte_size_text)
        except ValueError:
            pass
        else:
            if byte_size > 0 and byte_size < 37:
                return byte_size
        raise AssemblyError(
            "The first argument to POINT must be a decimal integer between 1 and 36."
        )

    @classmethod
    def convert_position(cls, position_text):
        """Return the value of the position argument."""
        if position_text is None:
            return 0
        try:
            position = int(position_text)
        except ValueError:
            pass
        else:
            if position > 0 and position < 37:
                return position
        raise AssemblyError(
            "The third argument to POINT must be a decimal integer between 1 and 36."
        )

    @classmethod
    def parse(cls, arguments):
        """Return the byte size, address and position from the argument."""
        split = arguments.split(",")
        if len(split) == 2:
            byte_size, address = split
            return byte_size, address
        if len(split) == 3:
            byte_size, address, position = split
            return byte_size, address, position
        raise AssemblyError(
            "The POINT pseudo op is formatted (decimal, address, decimal)."
        )

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = 1


class Iowd(PseudoOp):
    """The IOWD pseudo op."""

    name = "IOWD"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add an IO word to the program."""
        counter_text, address_text = cls.parse(source_line.arguments)
        counter = cls.convert_counter(assembler, counter_text)
        address = cls.convert_address(assembler, address_text)
        value = (counter << 18) | address
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=[value]
        )

    @classmethod
    def convert_counter(cls, assembler, text):
        """Return the value of the counter argument."""
        return ExpressionParser(text, assembler).as_half_word(negative=True)

    @classmethod
    def convert_address(cls, assembler, text):
        """Return the value of the address argument."""
        return ExpressionParser(text, assembler).as_half_word() - 1

    @classmethod
    def parse(cls, arguments):
        """Return counter and address arguments."""
        try:
            counter, address = arguments.split(",")
        except ValueError as e:
            raise AssemblyError("IOWD takes two arguments.").with_traceback(
                e.__traceback__
            ) from None
        else:
            return counter, address

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = 1


class Xwd(PseudoOp):
    """The XWD pseudo op."""

    name = "XWD"
    first_pass = False
    second_pass = True

    @classmethod
    def process(cls, assembler, source_line):
        """Add a word made of two half words to the program."""
        left_text, right_text = cls.parse(source_line.arguments)
        value = cls.get_value(left_text, right_text, assembler)
        assembler.current_pass.add_instructions(
            source_line=source_line, binary_values=[value]
        )

    @classmethod
    def get_value(cls, left_text, right_text, assembler):
        """Return the word created by combining the two half words."""
        left = ExpressionParser(left_text, assembler).as_half_word()
        right = ExpressionParser(right_text, assembler).as_half_word()
        return (left << 18) | right

    @classmethod
    def parse(cls, arguments):
        """Return left and right arguments."""
        try:
            left, right = arguments.split(",")
        except ValueError as e:
            raise AssemblyError("XWD takes two arguments.").with_traceback(
                e.__traceback__
            ) from None
        else:
            return left, right

    @classmethod
    def source_line_process(cls, source_line):
        """Update source line properties."""
        source_line.memory_location_count = 1
