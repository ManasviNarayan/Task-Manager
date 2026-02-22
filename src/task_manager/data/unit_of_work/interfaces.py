# task_manager/data/unit_of_work/interfaces.py
from task_manager.data.repositories.interfaces import ITaskRepository

from abc import ABC, abstractmethod

class ITaskUnitOfWork(ABC):
    @property
    @abstractmethod
    def tasks(self)-> ITaskRepository:
        pass

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass
