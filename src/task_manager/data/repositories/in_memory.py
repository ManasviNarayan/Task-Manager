"""
In-memory repository implementations for the Task Manager application.

This module provides concrete implementations of the repository interfaces
using Python lists and dictionaries for storage. These implementations
are suitable for development, testing, and demonstration purposes.
"""

from task_manager.data.repositories.interfaces import (
    ITaskRepository,
    ISubtaskRepository,
    IHistoryRepository,
)
from task_manager.infrastructure.in_memory import InMemoryDB
from task_manager.domain.models import Task, Subtask, History
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
from dataclasses import asdict
import logging

logger = get_logger(__name__, logging.ERROR)


class InMemoryTaskRepository(ITaskRepository):
    """
    In-memory implementation of task repository.
    
    Stores tasks in a Python list within the provided database object.
    This is a simple implementation suitable for development and testing.
    """

    def __init__(self, db: InMemoryDB) -> None:
        """
        Initialize the repository with a database object.
        
        Args:
            db: Database object containing tasks list.
        """
        self._db = db

    def get_tasks(self) -> list[Task]:
        """
        Retrieve all tasks from storage.
        
        Returns:
            List of all Task objects.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            tasks = [Task(**task) for task in self._db.tasks]
            logger.debug("Fetched %d tasks from in-memory DB", len(tasks))
            return tasks
        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching tasks: %s", str(e))
            raise DatabaseError("Failed to map stored task data to domain model")
        except Exception as e:
            logger.exception("Unexpected repository error in get_tasks")
            raise DatabaseError("Unexpected error while accessing tasks")

    def get_task(self, task_id: str) -> Task | None:
        """
        Retrieve a specific task by its ID.
        
        Args:
            task_id: Unique identifier of the task.
            
        Returns:
            Task object if found, None otherwise.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            task_data = next(
                (t for t in self._db.tasks if t["id"] == task_id),
                None,
            )
            if not task_data:
                logger.warning("Task with id %s not found in in-memory DB", task_id)
                return None
            return Task(**task_data)
        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching task id %s: %s", task_id, str(e))
            raise DatabaseError(
                f"Failed to map stored task data to domain model for id {task_id}"
            )
        except Exception as e:
            logger.exception(
                "Unexpected repository error in get_task for id %s", task_id
            )
            raise DatabaseError(f"Unexpected error while accessing task id {task_id}")

    def add_task(self, task: Task) -> Task:
        """
        Create a new task in storage.
        
        Args:
            task: Task object to create.
            
        Returns:
            The created task.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
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

    def update_task(self, task: Task) -> Task | None:
        """
        Update an existing task in storage.
        
        Args:
            task: Task object with updated fields (must include ID).
            
        Returns:
            Updated task if found, None if not found.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
        try:
            task_dict = asdict(task)
            for i, t in enumerate(self._db.tasks):
                if t["id"] == task.id:
                    self._db.tasks[i] = task_dict
                    logger.info("Updated task with id %s in in-memory DB", task.id)
                    return task
            logger.warning(
                "Task with id %s not found for update in in-memory DB", task.id
            )
            return None
        except (TypeError, ValueError) as e:
            logger.error("Data error while updating task: %s", str(e))
            raise DatabaseError("Failed to update task in storage")
        except Exception as e:
            logger.exception("Unexpected repository error in update_task")
            raise DatabaseError("Unexpected error while updating task")

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from storage.
        
        Args:
            task_id: Unique identifier of the task to delete.
            
        Returns:
            True if task was deleted, False if not found.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
        try:
            for i, t in enumerate(self._db.tasks):
                if t["id"] == task_id:
                    self._db.tasks.pop(i)
                    logger.info("Deleted task with id %s from in-memory DB", task_id)
                    return True
            logger.warning(
                "Task with id %s not found for deletion in in-memory DB", task_id
            )
            return False
        except Exception as e:
            logger.exception("Unexpected repository error in delete_task")
            raise DatabaseError("Unexpected error while deleting task")


class InMemorySubtaskRepository(ISubtaskRepository):
    """
    In-memory implementation of subtask repository.
    
    Stores subtasks in a Python list within the provided database object.
    """

    def __init__(self, db: InMemoryDB) -> None:
        """
        Initialize the repository with a database object.
        
        Args:
            db: Database object containing subtasks list.
        """
        self._db = db

    def get_subtasks(self, task_id: str) -> list[Subtask]:
        """
        Get all subtasks for a specific task.
        
        Args:
            task_id: ID of the parent task.
            
        Returns:
            List of Subtask objects belonging to the task.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            subtasks = [
                Subtask(**s)
                for s in self._db.subtasks
                if s["task_id"] == task_id
            ]
            logger.debug(
                "Fetched %d subtasks for task %s from in-memory DB",
                len(subtasks),
                task_id,
            )
            return subtasks
        except (TypeError, ValueError) as e:
            logger.error(
                "Data error while fetching subtasks for task %s: %s",
                task_id,
                str(e),
            )
            raise DatabaseError(
                "Failed to map stored subtask data to domain model"
            )
        except Exception as e:
            logger.exception(
                "Unexpected repository error in get_subtasks for task %s", task_id
            )
            raise DatabaseError("Unexpected error while accessing subtasks")

    def get_subtask(self, subtask_id: str) -> Subtask | None:
        """
        Retrieve a specific subtask by its ID.
        
        Args:
            subtask_id: Unique identifier of the subtask.
            
        Returns:
            Subtask object if found, None otherwise.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            subtask_data = next(
                (s for s in self._db.subtasks if s["id"] == subtask_id),
                None,
            )
            if not subtask_data:
                logger.warning(
                    "Subtask with id %s not found in in-memory DB", subtask_id
                )
                return None
            return Subtask(**subtask_data)
        except (TypeError, ValueError) as e:
            logger.error(
                "Data error while fetching subtask id %s: %s", subtask_id, str(e)
            )
            raise DatabaseError(
                f"Failed to map stored subtask data to domain model for id {subtask_id}"
            )
        except Exception as e:
            logger.exception(
                "Unexpected repository error in get_subtask for id %s", subtask_id
            )
            raise DatabaseError(
                f"Unexpected error while accessing subtask id {subtask_id}"
            )

    def add_subtask(self, subtask: Subtask) -> Subtask:
        """
        Create a new subtask in storage.
        
        Args:
            subtask: Subtask object to create.
            
        Returns:
            The created subtask.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
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
        """
        Update an existing subtask in storage.
        
        Args:
            subtask: Subtask object with updated fields.
            
        Returns:
            Updated subtask if found, None if not found.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
        try:
            subtask_dict = asdict(subtask)
            for i, s in enumerate(self._db.subtasks):
                if s["id"] == subtask.id:
                    self._db.subtasks[i] = subtask_dict
                    logger.info(
                        "Updated subtask with id %s in in-memory DB", subtask.id
                    )
                    return subtask
            logger.warning(
                "Subtask with id %s not found for update in in-memory DB",
                subtask.id,
            )
            return None
        except (TypeError, ValueError) as e:
            logger.error("Data error while updating subtask: %s", str(e))
            raise DatabaseError("Failed to update subtask in storage")
        except Exception as e:
            logger.exception("Unexpected repository error in update_subtask")
            raise DatabaseError("Unexpected error while updating subtask")

    def delete_subtask(self, subtask_id: str) -> bool:
        """
        Delete a subtask from storage.
        
        Args:
            subtask_id: Unique identifier of the subtask to delete.
            
        Returns:
            True if subtask was deleted, False if not found.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
        try:
            for i, s in enumerate(self._db.subtasks):
                if s["id"] == subtask_id:
                    self._db.subtasks.pop(i)
                    logger.info(
                        "Deleted subtask with id %s from in-memory DB", subtask_id
                    )
                    return True
            logger.warning(
                "Subtask with id %s not found for deletion in in-memory DB",
                subtask_id,
            )
            return False
        except Exception as e:
            logger.exception("Unexpected repository error in delete_subtask")
            raise DatabaseError("Unexpected error while deleting subtask")


class InMemoryHistoryRepository(IHistoryRepository):
    """
    In-memory implementation of history repository.
    
    Stores history entries in a Python list within the provided database object.
    Provides audit trail functionality for tasks and subtasks.
    """

    def __init__(self, db: InMemoryDB) -> None:
        """
        Initialize the repository with a database object.
        
        Args:
            db: Database object containing history list.
        """
        self._db = db

    def get_history(self, entity_id: str | None = None) -> list[History]:
        """
        Get history entries, optionally filtered by entity ID.
        
        Args:
            entity_id: Optional filter for specific entity.
                       If None, returns all history entries.
            
        Returns:
            List of History objects, filtered by entity_id if provided.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            if entity_id:
                history_entries = [
                    History(**h)
                    for h in self._db.history
                    if h["entity_id"] == entity_id
                ]
            else:
                history_entries = [History(**h) for h in self._db.history]
            logger.debug(
                "Fetched %d history entries from in-memory DB", len(history_entries)
            )
            return history_entries
        except (TypeError, ValueError) as e:
            logger.error("Data error while fetching history: %s", str(e))
            raise DatabaseError("Failed to map stored history data to domain model")
        except Exception as e:
            logger.exception("Unexpected repository error in get_history")
            raise DatabaseError("Unexpected error while accessing history")

    def get_history_for_task_subtasks(self, task_id: str) -> list[History]:
        """
        Get all history entries for a task's subtasks.
        
        This returns subtask-level history only (not task-level history).
        
        Args:
            task_id: ID of the parent task.
            
        Returns:
            List of History entries for subtasks of the task.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            subtask_ids = [
                s["id"] for s in self._db.subtasks if s["task_id"] == task_id
            ]
            history_entries = [
                History(**h)
                for h in self._db.history
                if h["entity_id"] in subtask_ids and h["entity_type"] == "subtask"
            ]
            logger.debug(
                "Fetched %d subtask history entries for task %s",
                len(history_entries),
                task_id,
            )
            return history_entries
        except (TypeError, ValueError) as e:
            logger.error(
                "Data error while fetching subtask history for task %s: %s",
                task_id,
                str(e),
            )
            raise DatabaseError(
                "Failed to map stored subtask history data to domain model"
            )
        except Exception as e:
            logger.exception(
                "Unexpected repository error in get_history_for_task_subtasks"
            )
            raise DatabaseError("Unexpected error while accessing subtask history")

    def get_history_for_subtask(self, subtask_id: str) -> list[History]:
        """
        Get all history entries for a specific subtask.
        
        Args:
            subtask_id: ID of the subtask.
            
        Returns:
            List of History entries for the subtask.
            
        Raises:
            DatabaseError: If data mapping fails or unexpected error occurs.
        """
        try:
            history_entries = [
                History(**h)
                for h in self._db.history
                if h["entity_id"] == subtask_id and h["entity_type"] == "subtask"
            ]
            logger.debug(
                "Fetched %d history entries for subtask %s",
                len(history_entries),
                subtask_id,
            )
            return history_entries
        except (TypeError, ValueError) as e:
            logger.error(
                "Data error while fetching history for subtask %s: %s",
                subtask_id,
                str(e),
            )
            raise DatabaseError(
                "Failed to map stored subtask history data to domain model"
            )
        except Exception as e:
            logger.exception(
                "Unexpected repository error in get_history_for_subtask"
            )
            raise DatabaseError("Unexpected error while accessing subtask history")

    def add_history(self, history: History) -> History:
        """
        Add a new history entry to storage.
        
        Args:
            history: History object to create.
            
        Returns:
            The created history entry.
            
        Raises:
            DatabaseError: If storage fails or unexpected error occurs.
        """
        try:
            history_dict = asdict(history)
            self._db.history.append(history_dict)
            logger.info(
                "Added history entry with id %s to in-memory DB", history.id
            )
            return history
        except (TypeError, ValueError) as e:
            logger.error("Data error while adding history: %s", str(e))
            raise DatabaseError("Failed to add history to storage")
        except Exception as e:
            logger.exception("Unexpected repository error in add_history")
            raise DatabaseError("Unexpected error while adding history")

