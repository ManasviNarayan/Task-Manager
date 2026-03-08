# exceptions.py
class ValidationError(Exception):
    """Raised when input validation fails."""
    pass

class NotFoundError(Exception):
    """Raised when a requested entity is not found."""
    pass

class DomainError(Exception):
    """Raised for general domain/business rule violations."""
    pass


class DomainValidationError(DomainError):
    """Raised when domain validation fails.
    
    This exception carries a list of validation errors rather than a single message,
    allowing clients to see all validation failures at once.
    """
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))

class DatabaseError(Exception):
    """Raised for database-related issues."""
    pass