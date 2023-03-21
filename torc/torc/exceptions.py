"""Custom exceptions defined in this package"""


class TorcBaseException(Exception):
    """Base exception for all exceptions in this package"""


class ExecutionError(TorcBaseException):
    """Raised if an error occurs while running a command."""


class InvalidParameter(TorcBaseException):
    """Raised if a parameter is invalid."""
