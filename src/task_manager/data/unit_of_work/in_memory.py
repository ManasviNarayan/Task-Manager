"""
In-memory Unit of Work implementations for the Task Manager application.

This module provides concrete implementations of the Unit of Work interfaces
using Python lists for storage. These implementations are suitable for
development, testing, and demonstration purposes.
"""

from typing import Any

from task_manager.data.repositories.in_memory import (
    InMemoryTaskRepository,
    InMemorySubtaskRepository,
    InMemoryHistoryRepository,
)
from task_manager.data.unit_of_work.interfaces import (
    ITaskUnitOfWork,
    ISubtaskUnitOfWork,
)
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
import logging

logger = get_logger(__name__, level=logging.INFO)


class InMemoryTaskUnitOfWork(ITaskUnitOfWork):
    """
    In-memory implementation of task Unit of Work.
    
    Provides transaction semantics for task, subtask, and history operations.
    In this implementation, commit and rollback are no-ops since changes
    are immediately applied to Python lists.
    """

    def __init__(self, db: Any) -> None:
        """
        Initialize the Unit of Work with a database object.
        
        Args:
            db: Database object containing tasks, subtasks, and history lists.
        """
        self._db = db
        self._tasks = InMemoryTaskRepository(db)
        self._subtasks = InMemorySubtaskRepository(db)
        self._history = InMemoryHistoryRepository(db)

    @property
    def tasks(self) -> InMemoryTaskRepository:
        """Get the task repository."""
        return self._tasks

    @property
    def subtasks(self) -> InMemorySubtaskRepository:
        """Get the subtask repository."""
        return self._subtasks

    @property
    def history(self) -> InMemoryHistoryRepository:
        """Get the history repository."""
        return self._history

    def __enter__(self) -> "InMemoryTaskUnitOfWork":
        """
        Enter the context manager.
        
        Returns:
            Self for use within the 'with' block.
        """
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """
        Exit the context manager.
        
        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception value if an exception was raised, None otherwise.
            exc_tb: Exception traceback if an exception was raised, None otherwise.
        """
        if exc_type is not None:
            self.rollback()
            logger.error(
                "Transaction rolled back due to exception: %s", exc_val
            )
        else:
            self.commit()

    def commit(self) -> None:
        """
        Commit the current transaction.
        
        Note:
            In-memory implementation - this is a no-op since changes
            are immediately applied to Python lists.
        """
        try:
            logger.debug("Committing transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Commit failed in InMemoryTaskUnitOfWork")
            raise DatabaseError("Commit failed in in-memory UoW") from e

    def rollback(self) -> None:
        """
        Rollback the current transaction.
        
        Note:
            In-memory implementation - this is a no-op since changes
            cannot be easily rolled back in Python lists.
        """
        try:
            logger.debug("Rolling back transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Rollback failed in InMemoryTaskUnitOfWork")
            raise DatabaseError("Rollback failed in in-memory UoW") from e


class InMemorySubtaskUnitOfWork(InMemoryTaskUnitOfWork):
    """
    In-memory Unit of Work for subtask operations.
    
    Inherits all properties (tasks, subtasks, history) from InMemoryTaskUnitOfWork.
    On commit/rollback, it automatically commits/rollbacks the parent class
    for atomic cross-UoW transactions.
    """

    def __init__(self, db: Any) -> None:
        """
        Initialize the Subtask Unit of Work with a database object.
        
        Args:
            db: Database object containing tasks, subtasks, and history lists.
        """
        super().__init__(db)

    def commit(self) -> None:
        """
        Commit the current transaction.
        
        Commits both the parent (InMemoryTaskUnitOfWork) and this UoW.
        
        Note:
            In-memory implementation - this is a no-op since changes
            are immediately applied to Python lists.
        """
        try:
            super().commit()
            logger.debug("Committing subtask transaction (in-memory no-op)")
        except Exception as e:
            self.rollback()
            logger.exception("Commit failed in InMemorySubtaskUnitOfWork")
            raise DatabaseError("Commit failed in in-memory subtask UoW") from e

    def rollback(self) -> None:
        """
        Rollback the current transaction.
        
        Rolls back both the parent (InMemoryTaskUnitOfWork) and this UoW.
        
        Note:
            In-memory implementation - this is a no-op since changes
            cannot be easily rolled back in Python lists.
        """
        try:
            super().rollback()
            logger.debug("Rolling back subtask transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Rollback failed in InMemorySubtaskUnitOfWork")
            raise DatabaseError("Rollback failed in in-memory subtask UoW") from e

