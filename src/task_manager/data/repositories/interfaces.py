# task_manager/data/repositories/interfaces.py
from abc import ABC, abstractmethod
from task_manager.domain.models import Task
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

