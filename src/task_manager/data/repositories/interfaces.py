from abc import ABC, abstractmethod
from typing import Iterable
class ITaskRepository(ABC):

    @abstractmethod
    def fetch_all_tasks(self)->Iterable:
        pass

