"""
Custom exceptions for the Task Manager application.

This module defines application-specific exception classes for
handling various error conditions in the Task Manager.
"""


class ValidationError(Exception):
    """
    Raised when input validation fails.

    This exception is used for validating user input or
    API request payloads.
    """

    pass


class NotFoundError(Exception):
    """
    Raised when a requested entity is not found.

    This exception is used when attempting to access a task,
    subtask, or other entity that does not exist.
    """

    pass


class DomainError(Exception):
    """
    Raised for general domain/business rule violations.

    This exception is used when an operation violates
    business rules or domain constraints.
    """

    pass


class DomainValidationError(DomainError):
    """
    Raised when domain validation fails.

    This exception carries a list of validation errors rather than
    a single message, allowing clients to see all validation
    failures at once.

    Attributes:
        errors: List of validation error messages.
    """

    def __init__(self, errors: list[str]) -> None:
        """
        Initialize the DomainValidationError.

        Args:
            errors: List of validation error messages.
        """
        self.errors = errors
        super().__init__("; ".join(errors))


class DatabaseError(Exception):
    """
    Raised for database-related issues.

    This exception is used when a database operation fails,
    such as connection issues or query errors.
    """

    pass

