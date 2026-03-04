# task_manager/data/unit_of_work/interfaces.py
from task_manager.data.repositories.interfaces import ITaskRepository
from typing import Self

from abc import ABC, abstractmethod

class ITaskUnitOfWork(ABC):
    @property
    @abstractmethod
    def tasks(self)-> ITaskRepository:
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
