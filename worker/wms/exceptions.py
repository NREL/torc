class WmsBaseException(Exception):
    """Base exception for all exceptions in this package"""


class ExecutionError(WmsBaseException):
    """Raised if an error occurs while running a command."""


class InvalidParameter(WmsBaseException):
    """Raised if a parameter is invalid."""
