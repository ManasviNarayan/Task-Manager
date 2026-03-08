"""
Dependency injection providers for the Task Manager API.

This module provides factory functions for creating Unit of Work
instances for dependency injection in the API handlers.
"""

from task_manager.data.unit_of_work.in_memory import (
    InMemorySubtaskUnitOfWork,
    InMemoryTaskUnitOfWork,
)
from task_manager.data.unit_of_work.interfaces import (
    ISubtaskUnitOfWork,
    ITaskUnitOfWork,
)
from task_manager.infrastructure.in_memory import InMemoryDB

_db = InMemoryDB()


def get_task_list_uow() -> ITaskUnitOfWork:
    """
    Factory function to create Task Unit of Work instances.

    This allows for proper dependency injection while maintaining
    the factory pattern for creating new instances per request.

    Returns:
        ITaskUnitOfWork: A new Task Unit of Work instance.
    """
    return InMemoryTaskUnitOfWork(_db)


def get_subtask_uow() -> ISubtaskUnitOfWork:
    """
    Factory function to create Subtask Unit of Work instances.

    Inherits from TaskUnitOfWork, so it has access to all repositories.
    On commit/rollback, it automatically commits/rollbacks the parent class.

    Returns:
        ISubtaskUnitOfWork: A new Subtask Unit of Work instance.
    """
    return InMemorySubtaskUnitOfWork(_db)

