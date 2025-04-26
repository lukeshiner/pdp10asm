"""The PseudoOperators class."""

from . import pseudo_ops as po


class PseudoOperators:
    """Class for handling assembler instructions."""

    instructions = {
        "LOC": po.Loc,
        "END": po.End,
        "TITLE": po.Title,
        "SUBTTLE": po.Subtitle,
        "RADIX": po.Radix,
        "EXP": po.Exp,
        "DEC": po.Dec,
        "OCT": po.Oct,
        "BYTE": po.Byte,
        "POINT": po.Point,
        "IOWD": po.Iowd,
        "XWD": po.Xwd,
        "ASCII": po.Ascii,
        "ASCIZ": po.Asciz,
        "SIXBIT": po.Sixbit,
    }

    @classmethod
    def is_pseudo_op(cls, name):
        """Return Truee if name is the name of a pseudo operator, otherwise False."""
        return name.upper() in cls.instructions

    @classmethod
    def get_pseudo_op(cls, name):
        """If name is the name of a pseudo operator return the operator, otherwise None."""
        try:
            return cls.instructions[name.upper()]
        except KeyError:
            return None
