# task_manager/data/repositories/interfaces.py
from abc import ABC, abstractmethod
from task_manager.domain.models import Task, Subtask, History
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


class ISubtaskRepository(ABC):

    @abstractmethod
    def get_subtasks(self, task_id: str) -> list[Subtask]:
        """Get all subtasks for a specific task."""
        pass

    @abstractmethod
    def get_subtask(self, subtask_id: str) -> Subtask | None:
        pass

    @abstractmethod
    def add_subtask(self, subtask: Subtask) -> Subtask:
        pass

    @abstractmethod
    def update_subtask(self, subtask: Subtask) -> Subtask | None:
        pass

    @abstractmethod
    def delete_subtask(self, subtask_id: str) -> bool:
        pass


class IHistoryRepository(ABC):
    
    @abstractmethod
    def get_history(self, entity_id: str | None = None) -> list[History]:
        """Get history entries, optionally filtered by entity_id."""
        pass

    @abstractmethod
    def get_history_for_task_subtasks(self, task_id: str) -> list[History]:
        """Get all history entries for a task's subtasks (not including task-level history)."""
        pass

    @abstractmethod
    def get_history_for_subtask(self, subtask_id: str) -> list[History]:
        """Get all history entries for a specific subtask."""
        pass

    @abstractmethod
    def add_history(self, history: History) -> History:
        """Add a new history entry."""
        pass

