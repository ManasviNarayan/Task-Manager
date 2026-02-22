# task_manager/data/repositories/in_memory/tasks.py
from task_manager.data.repositories.interfaces import ITaskRepository
from task_manager.domain.models import Task
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
import logging

logger = get_logger(__name__, logging.ERROR)

class InMemoryTaskRepository(ITaskRepository):
    def __init__(self, db):
        self._db = db

    def get_tasks(self)-> list[Task]:
        try:
            tasks = [Task(**task) for task in self._db.tasks]
            logger.debug("Fetched %d tasks from in-memory DB", len(tasks))
            return tasks

        except (TypeError, ValueError) as e:
            # Bad data in DB (wrong types, missing fields)
            logger.error("Data error while fetching tasks: %s", str(e))
            raise DatabaseError("Failed to map stored task data to domain model")

        except Exception as e:
            # Catch-all for unexpected persistence errors
            logger.exception("Unexpected repository error in get_tasks")
            raise DatabaseError("Unexpected error while accessing tasks")
