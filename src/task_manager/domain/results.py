"""
Result monad for functional error handling.

This module provides a simpler Result type that encapsulates either a success value
or an error. It follows the fail-accumulative pattern where all validation errors are
collected before returning.
"""
from typing import TypeVar, Generic, Callable

T = TypeVar('T')
U = TypeVar('U')


class Result(Generic[T]):
    """
    A monadic result type that either holds a success value or an error.
    
    This is a simpler implementation with map/bind for functional composition
    and combine for error accumulation.
    """
    
    def __init__(self, value=None, error=None):
        self._value = value
        self._error = error
    
    @staticmethod
    def Ok(value: T) -> 'Result[T]':
        """Create a successful Result with a value."""
        return Result(value=value)
    
    @staticmethod
    def Err(error: str) -> 'Result[T]':
        """Create an erroneous Result with an error."""
        return Result(error=error)
    
    def is_ok(self) -> bool:
        """Check if the result is successful (no error)."""
        return self._error is None
    
    def is_err(self) -> bool:
        """Check if the result contains an error."""
        return self._error is not None
    
    @property
    def value(self) -> T:
        """Get the success value. Raises if there are errors."""
        if self.is_err():
            raise ValueError(f"Cannot get value from erroneous Result: {self._error}")
        return self._value
    
    @property
    def error(self) -> str | None:
        """Get the error string."""
        return self._error
    
    def map(self, func: Callable[[T], U]) -> 'Result[U]':
        """Apply func to value if Ok, keep error otherwise."""
        if self.is_ok():
            try:
                return Result.Ok(func(self._value))
            except Exception as e:
                return Result.Err(str(e))
        return self  # type: ignore[return-value]
    
    def bind(self, func: Callable[[T], 'Result[U]']) -> 'Result[U]':
        """Chain a function that returns a Result."""
        if self.is_ok():
            try:
                return func(self._value)
            except Exception as e:
                return Result.Err(str(e))
        return self  # type: ignore[return-value]
    
    def __repr__(self) -> str:
        return f"Result(value={self._value}, error={self._error})"


def combine(*results: Result) -> Result:
    """
    Combine multiple Results into one.
    Returns Ok only if ALL results are Ok.
    Otherwise accumulates all errors.
    """
    all_errors: list[str] = []
    values: list = []
    
    for result in results:
        if result.is_err():
            if result.error:
                all_errors.append(result.error)
        else:
            values.append(result.value)
    
    if all_errors:
        return Result.Err("; ".join(all_errors))
    
    return Result.Ok(tuple(values))
