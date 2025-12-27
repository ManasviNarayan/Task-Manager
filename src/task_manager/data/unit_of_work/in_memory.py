# task_manager/data//in_memory/task_uow.py

from task_manager.data.repositories.in_memory import InMemoryTaskRepository
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork

class InMemoryTaskUnitOfWork(ITaskUnitOfWork):
    def __init__(self, db):
        self._db = db
        self._tasks = InMemoryTaskRepository(db)

    @property
    def tasks(self) :
        return self._tasks

    def commit(self):
        # In-memory has no real transaction, so pass
        pass

    def rollback(self):
        # Optional: clear DB or do nothing
        pass
