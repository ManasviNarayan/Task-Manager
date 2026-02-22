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

class DatabaseError(Exception):
    """Raised for database-related issues."""
    pass