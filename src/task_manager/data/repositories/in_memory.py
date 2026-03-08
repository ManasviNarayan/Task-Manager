# task_manager/data/repositories/in_memory/tasks.py
from task_manager.data.repositories.interfaces import ITaskRepository, IHistoryRepository
from task_manager.domain.models import Task, History
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
from dataclasses import asdict
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

    def get_task(self, task_id: str)-> Task|None:
        try:
            task_data = next((t for t in self._db.tasks if t['id'] == task_id), None)
            if not task_data:
                logger.warning("Task with id %s not found in in-memory DB", task_id)
                return None
            return Task(**task_data)

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching task id %s: %s", task_id, str(e))
            raise DatabaseError(f"Failed to map stored task data to domain model for id {task_id}")

        except Exception as e:
            logger.exception("Unexpected repository error in get_task for id %s", task_id)
            raise DatabaseError(f"Unexpected error while accessing task id {task_id}")

    def add_task(self, task: Task) -> Task:
        try:
            task_dict = asdict(task)
            self._db.tasks.append(task_dict)
            logger.info("Added task with id %s to in-memory DB", task.id)
            return task

        except (TypeError, ValueError) as e:
            logger.error("Data error while adding task: %s", str(e))
            raise DatabaseError("Failed to add task to storage")

        except Exception as e:
            logger.exception("Unexpected repository error in add_task")
            raise DatabaseError("Unexpected error while adding task")

    def update_task(self, task: Task) -> Task:
        try:
            task_dict = asdict(task)
            # Find and update the task in the list
            for i, t in enumerate(self._db.tasks):
                if t['id'] == task.id:
                    self._db.tasks[i] = task_dict
                    logger.info("Updated task with id %s in in-memory DB", task.id)
                    return task
            
            # Task not found
            logger.warning("Task with id %s not found for update in in-memory DB", task.id)
            return None

        except (TypeError, ValueError) as e:
            logger.error("Data error while updating task: %s", str(e))
            raise DatabaseError("Failed to update task in storage")

        except Exception as e:
            logger.exception("Unexpected repository error in update_task")
            raise DatabaseError("Unexpected error while updating task")

    def delete_task(self, task_id: str) -> bool:
        try:
            # Find and remove the task from the list
            for i, t in enumerate(self._db.tasks):
                if t['id'] == task_id:
                    self._db.tasks.pop(i)
                    logger.info("Deleted task with id %s from in-memory DB", task_id)
                    return True
            
            # Task not found
            logger.warning("Task with id %s not found for deletion in in-memory DB", task_id)
            return False

        except Exception as e:
            logger.exception("Unexpected repository error in delete_task")
            raise DatabaseError("Unexpected error while deleting task")


class InMemoryHistoryRepository(IHistoryRepository):
    def __init__(self, db):
        self._db = db

    def get_history(self, entity_id: str | None = None) -> list[History]:
        try:
            if entity_id:
                history_entries = [
                    History(**h) for h in self._db.history 
                    if h['entity_id'] == entity_id
                ]
            else:
                history_entries = [History(**h) for h in self._db.history]
            
            logger.debug("Fetched %d history entries from in-memory DB", len(history_entries))
            return history_entries

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching history: %s", str(e))
            raise DatabaseError("Failed to map stored history data to domain model")

        except Exception as e:
            logger.exception("Unexpected repository error in get_history")
            raise DatabaseError("Unexpected error while accessing history")

    def add_history(self, history: History) -> History:
        try:
            history_dict = asdict(history)
            self._db.history.append(history_dict)
            logger.info("Added history entry with id %s to in-memory DB", history.id)
            return history

        except (TypeError, ValueError) as e:
            logger.error("Data error while adding history: %s", str(e))
            raise DatabaseError("Failed to add history to storage")

        except Exception as e:
            logger.exception("Unexpected repository error in add_history")
            raise DatabaseError("Unexpected error while adding history")
