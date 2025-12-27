# task_manager/infrastructure/repositories/in_memory/tasks.py
from task_manager.data.repositories.interfaces import ITaskRepository

class InMemoryTaskRepository(ITaskRepository):
    def __init__(self, db):
        self._db = db

    def fetch_all_tasks(self):
        return self._db.tasks

