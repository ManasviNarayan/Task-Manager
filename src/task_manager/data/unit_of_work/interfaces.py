# task_manager/data/unit_of_work/interfaces.py
from task_manager.data.repositories.interfaces import ITaskRepository, ISubtaskRepository, IHistoryRepository
from typing import Self

from abc import ABC, abstractmethod

class ITaskUnitOfWork(ABC):
    @property
    @abstractmethod
    def tasks(self)-> ITaskRepository:
        pass

    @property
    @abstractmethod
    def subtasks(self) -> ISubtaskRepository:
        """Repository for subtasks."""
        pass

    @property
    @abstractmethod
    def history(self) -> IHistoryRepository:
        """Repository for history entries."""
        pass

    @abstractmethod
    def __enter__(self) -> Self:
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class ISubtaskUnitOfWork(ITaskUnitOfWork):
    """Subtask Unit of Work that inherits from TaskUnitOfWork.
    
    This provides a simpler interface - it inherits all properties from ITaskUnitOfWork.
    Uses the same underlying database as TaskUnitOfWork but can be used
    independently for subtask-focused operations.
    
    On commit/rollback, it automatically commits/rollbacks both itself and
    the parent class for atomic cross-UoW transactions.
    """
    pass
