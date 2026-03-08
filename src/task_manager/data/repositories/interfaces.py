# task_manager/data/repositories/interfaces.py
from abc import ABC, abstractmethod
from task_manager.domain.models import Task, History
from typing import Iterable

class ITaskRepository(ABC):

    @abstractmethod
    def get_tasks(self)->list[Task]:
        pass

    @abstractmethod
    def get_task(self, task_id: str)-> Task|None:
        pass

    @abstractmethod
    def add_task(self, task: Task)-> Task:
        pass

    @abstractmethod
    def update_task(self, task: Task) -> Task | None:
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        pass


class IHistoryRepository(ABC):
    
    @abstractmethod
    def get_history(self, entity_id: str | None = None) -> list[History]:
        """Get history entries, optionally filtered by entity_id."""
        pass

    @abstractmethod
    def add_history(self, history: History) -> History:
        """Add a new history entry."""
        pass

