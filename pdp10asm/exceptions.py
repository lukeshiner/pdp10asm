"""Exceptions for pdp10asm."""


class AssemblyError(ValueError):
    """Base exception class for errors in assembly."""


class ListingError(ValueError):
    """Base exception class for errors in creating listings."""
