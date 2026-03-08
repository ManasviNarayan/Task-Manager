"""
Subtask service for the Task Manager application.

This module contains the SubtaskService class which implements business logic
for subtask operations including CRUD, validation, and history tracking.
"""

import logging
import uuid
from datetime import datetime
from dataclasses import asdict

from task_manager.data.unit_of_work.interfaces import (
    ISubtaskUnitOfWork,
)
from task_manager.domain.models import History, HistoryType, Subtask
from task_manager.domain import pipelines
from task_manager.exceptions import (
    DatabaseError,
    DomainError,
    DomainValidationError,
    NotFoundError,
    ValidationError,
)
from task_manager.logger import get_logger

logger = get_logger(__name__, logging.INFO)


class SubtaskService:
    """
    Service for managing subtasks and their operations.

    This service handles all business logic related to subtasks including
    validation, CRUD operations, and history tracking. It maintains
    cross-references with parent tasks for validation purposes.
    """

    def __init__(
        self,
        subtask_uow: ISubtaskUnitOfWork,
    ) -> None:
        """
        Initialize the SubtaskService with Unit of Work instance.

        Args:
            subtask_uow: Unit of Work for subtask data access operations.
                         Inherits from ITaskUnitOfWork, so provides access
                         to tasks, subtasks, and history repositories.
        """
        self.subtask_uow = subtask_uow

    def _record_history(
        self,
        entity_id: str,
        entity_type: str,
        change_type: HistoryType,
        old_value: str | None,
        new_value: str | None,
    ) -> None:
        """
        Record a history entry for a subtask change.

        Args:
            entity_id: ID of the subtask that was changed.
            entity_type: Type of entity ("subtask").
            change_type: Type of change that occurred.
            old_value: Previous state as JSON string.
            new_value: New state as JSON string.
        """
        history_entry = History(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            entity_type=entity_type,
            change_type=change_type,
            timestamp=datetime.now(),
            old_value=old_value,
            new_value=new_value,
        )
        self.subtask_uow.history.add_history(history_entry)

    def _record_task_history(
        self,
        task_id: str,
        change_type: HistoryType,
        old_subtask_count: int,
        new_subtask_count: int,
    ) -> None:
        """
        Record task-side history with subtask count changes.

        This is used when a subtask operation affects the parent task.
        The history entry has entity_type="task" with subtask count
        in old/new values.

        Args:
            task_id: ID of the parent task.
            change_type: Type of change that occurred.
            old_subtask_count: Number of subtasks before the change.
            new_subtask_count: Number of subtasks after the change.
        """
        history_entry = History(
            id=str(uuid.uuid4()),
            entity_id=task_id,
            entity_type="task",
            change_type=change_type,
            timestamp=datetime.now(),
            old_value=f"{old_subtask_count} subtasks",
            new_value=f"{new_subtask_count} subtasks",
        )
        self.subtask_uow.history.add_history(history_entry)

    def get_subtasks(self, task_id: str) -> list[Subtask]:
        """
        Retrieve all subtasks for a specific task.

        Args:
            task_id: Unique identifier of the parent task.

        Returns:
            List of all Subtask objects for the given task.

        Raises:
            NotFoundError: If the parent task is not found.
            DomainError: If an unexpected error occurs.
        """
        try:
            task = self.subtask_uow.tasks.get_task(task_id)
            if not task:
                logger.warning(
                    "Task with id %s not found in repository", task_id
                )
                raise NotFoundError(f"Task with id {task_id} not found")

            subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            logger.info(
                "Fetched %d subtasks for task %s", len(subtasks), task_id
            )
            return subtasks

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(
                "Database error in get_subtasks for task %s: %s",
                task_id,
                str(e),
            )
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error in SubtaskService.get_subtasks for task %s",
                task_id,
            )
            raise DomainError("Service failed to fetch subtasks") from e

    def get_subtask(self, subtask_id: str) -> Subtask:
        """
        Retrieve a specific subtask by its ID.

        Args:
            subtask_id: Unique identifier of the subtask.

        Returns:
            The Subtask object.

        Raises:
            NotFoundError: If the subtask is not found.
            DomainError: If an unexpected error occurs.
        """
        try:
            subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not subtask:
                logger.warning(
                    "Subtask with id %s not found in repository", subtask_id
                )
                raise NotFoundError(f"Subtask with id {subtask_id} not found")

            logger.info("Fetched subtask with id %s", subtask_id)
            return subtask

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(
                "Database error in get_subtask for id %s: %s",
                subtask_id,
                str(e),
            )
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error in SubtaskService.get_subtask for id %s",
                subtask_id,
            )
            raise DomainError(
                f"Service failed to fetch subtask with id {subtask_id}"
            ) from e

    def create_subtask(self, task_id: str, subtask: Subtask) -> Subtask:
        """
        Create a new subtask for a task.

        Validates that the parent task exists and that the subtask's
        deadline does not exceed the parent task's deadline.

        Args:
            task_id: Unique identifier of the parent task.
            subtask: Subtask object to create.

        Returns:
            The created subtask with generated ID.

        Raises:
            NotFoundError: If the parent task is not found.
            DomainValidationError: If validation fails.
            ValidationError: If a business rule is violated.
            DomainError: If an unexpected error occurs.
        """
        try:
            task = self.subtask_uow.tasks.get_task(task_id)
            if not task:
                logger.warning(
                    "Task with id %s not found for subtask creation", task_id
                )
                raise NotFoundError(f"Task with id {task_id} not found")

            validation_result = pipelines.subtask_create_validation_pipeline(
                parent_deadline=task.deadline,
                subtask_deadline=subtask.deadline,
            )

            if validation_result.is_err():
                error_msg = validation_result.error or "Validation failed"
                raise DomainValidationError([error_msg])

            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)

            if not subtask.id:
                subtask.id = str(uuid.uuid4())

            subtask.task_id = task_id

            created_subtask = self.subtask_uow.subtasks.add_subtask(subtask)

            if created_subtask.id is None:
                raise DomainError("Failed to create subtask - no ID generated")
            new_value = asdict(created_subtask)
            self._record_history(
                entity_id=created_subtask.id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_CREATED,
                old_value=None,
                new_value=str(new_value),
            )

            new_count = old_count + 1
            self._record_task_history(
                task_id,
                HistoryType.SUBTASK_CREATED,
                old_count,
                new_count,
            )

            logger.info(
                "Created subtask with id %s for task %s", subtask.id, task_id
            )
            return created_subtask

        except (NotFoundError, DomainValidationError):
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
        """
        Update an existing subtask.

        Validates that the subtask exists and that any deadline or status
        changes comply with parent task constraints.

        Args:
            subtask_id: ID of the subtask to update.
            subtask: Subtask object with updated fields.

        Returns:
            The updated subtask.

        Raises:
            NotFoundError: If the subtask or parent task is not found.
            DomainValidationError: If validation fails.
            DomainError: If an unexpected error occurs.
        """
        try:
            existing_subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not existing_subtask:
                logger.warning(
                    "Subtask with id %s not found for update", subtask_id
                )
                raise NotFoundError(f"Subtask with id {subtask_id} not found")

            task_id = existing_subtask.task_id

            parent_task = self.subtask_uow.tasks.get_task(task_id)
            if not parent_task:
                raise NotFoundError(f"Parent task with id {task_id} not found")

            validation_result = pipelines.subtask_update_validation_pipeline(
                parent_task=parent_task,
                old_subtask=existing_subtask,
                new_deadline=subtask.deadline,
                new_status=subtask.status,
            )

            if validation_result.is_err():
                error_msg = validation_result.error or "Validation failed"
                raise DomainValidationError([error_msg])

            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)

            old_value = asdict(existing_subtask)

            subtask.id = subtask_id
            subtask.task_id = task_id
            updated_subtask = self.subtask_uow.subtasks.update_subtask(subtask)

            if updated_subtask is None:
                raise DomainError(
                    f"Failed to update subtask with id {subtask_id}"
                )

            new_value = asdict(updated_subtask)
            self._record_history(
                entity_id=subtask_id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_UPDATED,
                old_value=str(old_value),
                new_value=str(new_value),
            )

            self._record_task_history(
                task_id, HistoryType.SUBTASK_UPDATED, old_count, old_count
            )

            logger.info("Updated subtask with id %s", subtask_id)
            return updated_subtask

        except (NotFoundError, DomainValidationError):
            raise

        except DatabaseError as e:
            logger.error("Database error in update_subtask: %s", str(e))
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error in SubtaskService.update_subtask"
            )
            raise DomainError("Service failed to update subtask") from e

    def get_subtasks_history(self, task_id: str) -> list[History]:
        """
        Get all history entries for a task's subtasks.

        Retrieves history entries for all subtasks belonging to the
        specified parent task.

        Args:
            task_id: Unique identifier of the parent task.

        Returns:
            List of History entries for the task's subtasks.

        Raises:
            NotFoundError: If the parent task is not found.
            DomainError: If an unexpected error occurs.
        """
        try:
            task = self.subtask_uow.tasks.get_task(task_id)
            if not task:
                logger.warning(
                    "Task with id %s not found in repository", task_id
                )
                raise NotFoundError(f"Task with id {task_id} not found")

            history = self.subtask_uow.history.get_history_for_task_subtasks(
                task_id
            )
            logger.info(
                "Fetched %d subtask history entries for task %s",
                len(history),
                task_id,
            )
            return history

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(
                "Database error in get_subtasks_history for task %s: %s",
                task_id,
                str(e),
            )
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error in SubtaskService.get_subtasks_history "
                "for task %s",
                task_id,
            )
            raise DomainError("Service failed to fetch subtasks history") from e

    def get_subtask_history(self, subtask_id: str) -> list[History]:
        """
        Get all history entries for a specific subtask.

        Args:
            subtask_id: Unique identifier of the subtask.

        Returns:
            List of History entries for the subtask.

        Raises:
            NotFoundError: If the subtask is not found.
            DomainError: If an unexpected error occurs.
        """
        try:
            subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not subtask:
                logger.warning(
                    "Subtask with id %s not found in repository", subtask_id
                )
                raise NotFoundError(f"Subtask with id {subtask_id} not found")

            history = self.subtask_uow.history.get_history_for_subtask(
                subtask_id
            )
            logger.info(
                "Fetched %d history entries for subtask %s",
                len(history),
                subtask_id,
            )
            return history

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error(
                "Database error in get_subtask_history for subtask %s: %s",
                subtask_id,
                str(e),
            )
            raise

        except Exception as e:
            logger.exception(
                "Unexpected error in SubtaskService.get_subtask_history "
                "for subtask %s",
                subtask_id,
            )
            raise DomainError("Service failed to fetch subtask history") from e

    def delete_subtask(self, subtask_id: str) -> bool:
        """
        Delete a subtask.

        Args:
            subtask_id: ID of the subtask to delete.

        Returns:
            True if the subtask was deleted.

        Raises:
            NotFoundError: If the subtask is not found.
            DomainError: If an unexpected error occurs.
        """
        try:
            existing_subtask = self.subtask_uow.subtasks.get_subtask(subtask_id)
            if not existing_subtask:
                logger.warning(
                    "Subtask with id %s not found for deletion", subtask_id
                )
                raise NotFoundError(f"Subtask with id {subtask_id} not found")

            task_id = existing_subtask.task_id

            old_subtasks = self.subtask_uow.subtasks.get_subtasks(task_id)
            old_count = len(old_subtasks)

            old_value = asdict(existing_subtask)

            result = self.subtask_uow.subtasks.delete_subtask(subtask_id)

            self._record_history(
                entity_id=subtask_id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_DELETED,
                old_value=str(old_value),
                new_value=None,
            )

            new_count = old_count - 1
            self._record_task_history(
                task_id, HistoryType.SUBTASK_DELETED, old_count, new_count
            )

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

