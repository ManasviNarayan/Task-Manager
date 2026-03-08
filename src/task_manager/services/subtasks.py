# task_manager/services/subtasks.py
from task_manager.data.unit_of_work.interfaces import ISubtaskUnitOfWork, ITaskUnitOfWork
from task_manager.domain.models import Subtask, History, HistoryType
from task_manager.exceptions import DatabaseError, DomainError, NotFoundError, ValidationError
from task_manager.logger import get_logger
from dataclasses import asdict
import logging
import uuid
from datetime import datetime

logger = get_logger(__name__, logging.INFO)


class SubtaskService:

    def __init__(self, subtask_uow: ISubtaskUnitOfWork, task_uow: ITaskUnitOfWork = None):
        """Initialize SubtaskService with subt.
        
        Argsask UoW:
            subtask_uow: The subtask Unit of Work for subtask operations
            task_uow: Optional task Unit of Work for cross-UoW operations.
                     If provided, used for recording task-side history.
        """
        self.subtask_uow = subtask_uow
        self.task_uow = task_uow  # Optional - for cross-UoW transactions

    def _record_history(self, entity_id: str, entity_type: str, change_type: HistoryType, old_value: str | None, new_value: str | None):
        """Helper method to record a history entry."""
        from task_manager.domain.models import History
        history_entry = History(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            entity_type=entity_type,
            change_type=change_type,
            timestamp=datetime.now(),
            old_value=old_value,
            new_value=new_value
        )
        self.subtask_uow.history.add_history(history_entry)

    def _record_task_history(self, task_id: str, change_type: HistoryType, old_subtask_count: int, new_subtask_count: int):
        """Record task-side history with subtask count changes.
        
        This is used when a subtask operation affects the parent task.
        The history entry has entity_type="task" with subtask count in old/new values.
        """
        if self.task_uow is None:
            logger.warning("Task UoW not provided, skipping task-side history recording")
            return
            
        from task_manager.domain.models import History
        history_entry = History(
            id=str(uuid.uuid4()),
            entity_id=task_id,
            entity_type="task",
            change_type=change_type,
            timestamp=datetime.now(),
            old_value=f"{old_subtask_count} subtasks",
            new_value=f"{new_subtask_count} subtasks"
        )
        self.task_uow.history.add_history(history_entry)

    def get_subtasks(self, task_id: str) -> list[Subtask]:
        """Get all subtasks for a specific task."""
        try:
            # Verify task exists (need task_uow for this)
            if self.task_uow is None:
                raise DomainError("Task UoW required to verify parent task exists")
            
            task = self.task_uow.tasks.get_task(task_id)
            if not task:
                logger.warning("Task with id %s not found in repository", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            logger.info("Fetched %d subtasks for task %s", len(subtasks), task_id)
            return subtasks

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in get_subtasks for task %s: %s", task_id, str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.get_subtasks for task %s", task_id)
            raise DomainError("Service failed to fetch subtasks") from e

    def get_subtask(self, subtask_id: str) -> Subtask:
        """Get a specific subtask by ID."""
        try:
            subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not subtask:
                logger.warning("Subtask with id %s not found in repository", subtask_id)
                raise NotFoundError(f"Subtask with id {subtask_id} not found")
            
            logger.info("Fetched subtask with id %s", subtask_id)
            return subtask

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in get_subtask for id %s: %s", subtask_id, str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.get_subtask for id %s", subtask_id)
            raise DomainError(f"Service failed to fetch subtask with id {subtask_id}") from e

    def create_subtask(self, task_id: str, subtask: Subtask) -> Subtask:
        """Create a new subtask for a task."""
        try:
            # Verify task exists (need task_uow for this)
            if self.task_uow is None:
                raise DomainError("Task UoW required to verify parent task exists")
            
            task = self.task_uow.tasks.get_task(task_id)
            if not task:
                logger.warning("Task with id %s not found for subtask creation", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            # Get old subtask count for history
            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)
            
            # Generate ID if not provided
            if not subtask.id:
                subtask.id = str(uuid.uuid4())
            
            # Set the task_id
            subtask.task_id = task_id
            
            # Add subtask through repository
            created_subtask = self.subtask_uow.subtasks.add_subtask(subtask)
            
            # Record subtask history
            if created_subtask.id is None:
                raise DomainError("Failed to create subtask - no ID generated")
            new_value = asdict(created_subtask)
            self._record_history(
                entity_id=created_subtask.id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_CREATED,
                old_value=None,
                new_value=str(new_value)
            )
            
            # Record task-side history with subtask count
            new_count = old_count + 1
            self._record_task_history(task_id, HistoryType.SUBTASK_CREATED, old_count, new_count)
            
            logger.info("Created subtask with id %s for task %s", subtask.id, task_id)
            return created_subtask

        except NotFoundError:
            raise

        except ValidationError:
            raise

        except DatabaseError as e:
            logger.error("Database error in create_subtask: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.create_subtask")
            raise DomainError("Service failed to create subtask") from e

    def update_subtask(self, subtask_id: str, subtask: Subtask) -> Subtask:
        """Update an existing subtask."""
        try:
            # Check if subtask exists
            existing_subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not existing_subtask:
                logger.warning("Subtask with id %s not found for update", subtask_id)
                raise NotFoundError(f"Subtask with id {subtask_id} not found")
            
            # Get task_id for history
            task_id = existing_subtask.task_id
            
            # Get old subtask count for history
            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)
            
            # Capture old value for history
            old_value = asdict(existing_subtask)
            
            # Update the subtask with the provided ID
            subtask.id = subtask_id
            subtask.task_id = task_id
            updated_subtask = self.subtask_uow.subtasks.update_subtask(subtask)
            
            if updated_subtask is None:
                raise DomainError(f"Failed to update subtask with id {subtask_id}")
            
            # Record subtask history
            new_value = asdict(updated_subtask)
            self._record_history(
                entity_id=subtask_id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_UPDATED,
                old_value=str(old_value),
                new_value=str(new_value)
            )
            
            # Record task-side history with subtask count (FIX: was missing before)
            self._record_task_history(task_id, HistoryType.SUBTASK_UPDATED, old_count, old_count)
            
            logger.info("Updated subtask with id %s", subtask_id)
            return updated_subtask

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in update_subtask: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.update_subtask")
            raise DomainError("Service failed to update subtask") from e

    def get_subtasks_history(self, task_id: str) -> list[History]:
        """Get all history entries for a task's subtasks."""
        try:
            # Verify task exists
            if self.task_uow is None:
                raise DomainError("Task UoW required to verify parent task exists")
            
            task = self.task_uow.tasks.get_task(task_id)
            if not task:
                logger.warning("Task with id %s not found in repository", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            # Get subtask history for this task
            history = self.subtask_uow.history.get_history_for_task_subtasks(task_id)
            logger.info("Fetched %d subtask history entries for task %s", len(history), task_id)
            return history

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in get_subtasks_history for task %s: %s", task_id, str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.get_subtasks_history for task %s", task_id)
            raise DomainError("Service failed to fetch subtasks history") from e

    def get_subtask_history(self, subtask_id: str) -> list[History]:
        """Get all history entries for a specific subtask."""
        try:
            # Verify subtask exists
            subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not subtask:
                logger.warning("Subtask with id %s not found in repository", subtask_id)
                raise NotFoundError(f"Subtask with id {subtask_id} not found")
            
            # Get history for this subtask
            history = self.subtask_uow.history.get_history_for_subtask(subtask_id)
            logger.info("Fetched %d history entries for subtask %s", len(history), subtask_id)
            return history

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in get_subtask_history for subtask %s: %s", subtask_id, str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.get_subtask_history for subtask %s", subtask_id)
            raise DomainError("Service failed to fetch subtask history") from e

    def delete_subtask(self, subtask_id: str) -> bool:
        """Delete a subtask."""
        try:
            # Check if subtask exists
            existing_subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not existing_subtask:
                logger.warning("Subtask with id %s not found for deletion", subtask_id)
                raise NotFoundError(f"Subtask with id {subtask_id} not found")
            
            # Get task_id before deletion for history
            task_id = existing_subtask.task_id
            
            # Get old subtask count for history
            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)
            
            # Capture old value for history before deletion
            old_value = asdict(existing_subtask)
            
            # Delete the subtask
            result = self.subtask_uow.subtasks.delete_subtask(subtask_id)
            
            # Record subtask history
            self._record_history(
                entity_id=subtask_id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_DELETED,
                old_value=str(old_value),
                new_value=None
            )
            
            # Record task-side history with subtask count
            new_count = old_count - 1
            self._record_task_history(task_id, HistoryType.SUBTASK_DELETED, old_count, new_count)
            
            logger.info("Deleted subtask with id %s", subtask_id)
            return result

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in delete_subtask: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in SubtaskService.delete_subtask")
            raise DomainError("Service failed to delete subtask") from e

