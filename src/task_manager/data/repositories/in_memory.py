# task_manager/data/repositories/in_memory/tasks.py
from task_manager.data.repositories.interfaces import ITaskRepository, ISubtaskRepository, IHistoryRepository
from task_manager.domain.models import Task, Subtask, History
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


class InMemorySubtaskRepository(ISubtaskRepository):
    def __init__(self, db):
        self._db = db

    def get_subtasks(self, task_id: str) -> list[Subtask]:
        try:
            subtasks = [Subtask(**s) for s in self._db.subtasks if s['task_id'] == task_id]
            logger.debug("Fetched %d subtasks for task %s from in-memory DB", len(subtasks), task_id)
            return subtasks

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching subtasks for task %s: %s", task_id, str(e))
            raise DatabaseError("Failed to map stored subtask data to domain model")

        except Exception as e:
            logger.exception("Unexpected repository error in get_subtasks for task %s", task_id)
            raise DatabaseError("Unexpected error while accessing subtasks")

    def get_subtask(self, subtask_id: str) -> Subtask | None:
        try:
            subtask_data = next((s for s in self._db.subtasks if s['id'] == subtask_id), None)
            if not subtask_data:
                logger.warning("Subtask with id %s not found in in-memory DB", subtask_id)
                return None
            return Subtask(**subtask_data)

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching subtask id %s: %s", subtask_id, str(e))
            raise DatabaseError(f"Failed to map stored subtask data to domain model for id {subtask_id}")

        except Exception as e:
            logger.exception("Unexpected repository error in get_subtask for id %s", subtask_id)
            raise DatabaseError(f"Unexpected error while accessing subtask id {subtask_id}")

    def add_subtask(self, subtask: Subtask) -> Subtask:
        try:
            subtask_dict = asdict(subtask)
            self._db.subtasks.append(subtask_dict)
            logger.info("Added subtask with id %s to in-memory DB", subtask.id)
            return subtask

        except (TypeError, ValueError) as e:
            logger.error("Data error while adding subtask: %s", str(e))
            raise DatabaseError("Failed to add subtask to storage")

        except Exception as e:
            logger.exception("Unexpected repository error in add_subtask")
            raise DatabaseError("Unexpected error while adding subtask")

    def update_subtask(self, subtask: Subtask) -> Subtask | None:
        try:
            subtask_dict = asdict(subtask)
            # Find and update the subtask in the list
            for i, s in enumerate(self._db.subtasks):
                if s['id'] == subtask.id:
                    self._db.subtasks[i] = subtask_dict
                    logger.info("Updated subtask with id %s in in-memory DB", subtask.id)
                    return subtask
            
            # Subtask not found
            logger.warning("Subtask with id %s not found for update in in-memory DB", subtask.id)
            return None

        except (TypeError, ValueError) as e:
            logger.error("Data error while updating subtask: %s", str(e))
            raise DatabaseError("Failed to update subtask in storage")

        except Exception as e:
            logger.exception("Unexpected repository error in update_subtask")
            raise DatabaseError("Unexpected error while updating subtask")

    def delete_subtask(self, subtask_id: str) -> bool:
        try:
            # Find and remove the subtask from the list
            for i, s in enumerate(self._db.subtasks):
                if s['id'] == subtask_id:
                    self._db.subtasks.pop(i)
                    logger.info("Deleted subtask with id %s from in-memory DB", subtask_id)
                    return True
            
            # Subtask not found
            logger.warning("Subtask with id %s not found for deletion in in-memory DB", subtask_id)
            return False

        except Exception as e:
            logger.exception("Unexpected repository error in delete_subtask")
            raise DatabaseError("Unexpected error while deleting subtask")


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

    def get_history_for_task_subtasks(self, task_id: str) -> list[History]:
        """Get all history entries for a task's subtasks."""
        try:
            # Get all subtask IDs for this task
            subtask_ids = [s['id'] for s in self._db.subtasks if s['task_id'] == task_id]
            
            # Get history entries where entity_id is one of the subtask IDs
            history_entries = [
                History(**h) for h in self._db.history 
                if h['entity_id'] in subtask_ids and h['entity_type'] == 'subtask'
            ]
            
            logger.debug("Fetched %d subtask history entries for task %s", len(history_entries), task_id)
            return history_entries

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching subtask history for task %s: %s", task_id, str(e))
            raise DatabaseError("Failed to map stored subtask history data to domain model")

        except Exception as e:
            logger.exception("Unexpected repository error in get_history_for_task_subtasks")
            raise DatabaseError("Unexpected error while accessing subtask history")

    def get_history_for_subtask(self, subtask_id: str) -> list[History]:
        """Get all history entries for a specific subtask."""
        try:
            history_entries = [
                History(**h) for h in self._db.history 
                if h['entity_id'] == subtask_id and h['entity_type'] == 'subtask'
            ]
            
            logger.debug("Fetched %d history entries for subtask %s", len(history_entries), subtask_id)
            return history_entries

        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching history for subtask %s: %s", subtask_id, str(e))
            raise DatabaseError("Failed to map stored subtask history data to domain model")

        except Exception as e:
            logger.exception("Unexpected repository error in get_history_for_subtask")
            raise DatabaseError("Unexpected error while accessing subtask history")

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
