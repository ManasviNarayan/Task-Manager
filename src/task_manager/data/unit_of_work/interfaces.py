"""
Unit of Work interfaces for the Task Manager application.

This module defines abstract Unit of Work interfaces that coordinate
multiple repositories and manage transaction boundaries. The UoW pattern
ensures atomic operations across different data stores.
"""

from abc import ABC, abstractmethod
from typing import Self

from task_manager.data.repositories.interfaces import (
    ITaskRepository,
    ISubtaskRepository,
    IHistoryRepository,
)


class ITaskUnitOfWork(ABC):
    """
    Abstract interface for task-related Unit of Work.
    
    Coordinates access to tasks, subtasks, and history repositories
    while providing transaction semantics (commit/rollback).
    
    Implementations should support the context manager protocol
    (__enter__/__exit__) for automatic transaction management.
    """

    @property
    @abstractmethod
    def tasks(self) -> ITaskRepository:
        """
        Get the task repository.
        
        Returns:
            Repository for task CRUD operations.
        """
        pass

    @property
    @abstractmethod
    def subtasks(self) -> ISubtaskRepository:
        """
        Get the subtask repository.
        
        Returns:
            Repository for subtask CRUD operations.
        """
        pass

    @property
    @abstractmethod
    def history(self) -> IHistoryRepository:
        """
        Get the history repository.
        
        Returns:
            Repository for history/audit log operations.
        """
        pass

    @abstractmethod
    def __enter__(self) -> Self:
        """
        Enter the context manager.
        
        Returns:
            Self for use within the 'with' block.
        """
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit the context manager.
        
        Args:
            exc_type: Exception type if an exception was raised, None otherwise.
            exc_val: Exception value if an exception was raised, None otherwise.
            exc_tb: Exception traceback if an exception was raised, None otherwise.
            
        Note:
            Should commit on success, rollback on exception.
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """
        Commit the current transaction.
        
        All changes made through repositories since the last
        commit/rollback should be persisted.
        """
        pass

    @abstractmethod
    def rollback(self) -> None:
        """
        Rollback the current transaction.
        
        All changes made through repositories since the last
        commit/rollback should be discarded.
        """
        pass


class ISubtaskUnitOfWork(ITaskUnitOfWork):
    """
    Subtask Unit of Work that inherits from TaskUnitOfWork.
    
    This provides a simpler interface - it inherits all properties from ITaskUnitOfWork.
    Uses the same underlying database as TaskUnitOfWork but can be used
    independently for subtask-focused operations.
    
    On commit/rollback, it automatically commits/rollbacks both itself and
    the parent class for atomic cross-UoW transactions.
    """

