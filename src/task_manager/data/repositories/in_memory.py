# task_manager/infrastructure/repositories/in_memory/tasks.py
from task_manager.data.repositories.interfaces import ITaskRepository
from task_manager.domain.models import Task

class InMemoryTaskRepository(ITaskRepository):
    def __init__(self, db):
        self._db = db

    def get_tasks(self):
        tasks = [Task(**task) for task in self._db.tasks]
        return tasks

