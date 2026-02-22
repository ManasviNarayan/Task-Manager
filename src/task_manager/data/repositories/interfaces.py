from abc import ABC, abstractmethod
from typing import Iterable
class ITaskRepository(ABC):

    @abstractmethod
    def get_tasks(self)->Iterable:
        pass

