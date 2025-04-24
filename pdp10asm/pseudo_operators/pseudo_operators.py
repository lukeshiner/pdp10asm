"""The PseudoOperators class."""

from .pseudo_ops import PseudoOp


class PseudoOperators:
    """Class for handling assembler instructions."""

    instructions = {
        pseudo_op.name: pseudo_op for pseudo_op in PseudoOp.__subclasses__()
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
