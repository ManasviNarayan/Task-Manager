# task_manager/services/tasks.py
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.domain.models import Task, Subtask, History, HistoryType, Status
from task_manager.domain import pipelines
from task_manager.exceptions import DatabaseError, DomainError, NotFoundError, ValidationError, DomainValidationError
from task_manager.logger import get_logger
from dataclasses import asdict
import logging
import uuid
from datetime import datetime

logger = get_logger(__name__, logging.INFO)

class TaskService:

    def __init__(self, task_uow: ITaskUnitOfWork):
        self.task_uow = task_uow

    def _record_history(self, entity_id: str, entity_type: str, change_type: HistoryType, old_value: str | None, new_value: str | None):
        """Helper method to record a history entry."""
        history_entry = History(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            entity_type=entity_type,
            change_type=change_type,
            timestamp=datetime.now(),
            old_value=old_value,
            new_value=new_value
        )
        self.task_uow.history.add_history(history_entry)

    def get_tasks(self)-> list[Task]:
        try:
            tasks = self.task_uow.tasks.get_tasks()
            logger.info("Fetched %d tasks from repository", len(tasks))
            return tasks

        except DatabaseError as e:
            logger.error("Database error in get_tasks: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.get_tasks")
            raise DomainError("Service failed to fetch tasks") from e

    def get_task(self, task_id: str)-> Task:
        try:
            task = self.task_uow.tasks.get_task(task_id)
            if not task:
                logger.warning("Task with id %s not found in repository", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            logger.info("Fetched task with id %s from repository", task_id)
            return task

        except DatabaseError as e:
            logger.error("Database error in get_task for id %s: %s", task_id, str(e))
            raise

        except NotFoundError:
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.get_task for id %s", task_id)
            raise DomainError(f"Service failed to fetch task with id {task_id}") from e

    def get_task_history(self, task_id: str = None) -> list[History]:
        """Get history entries for a specific task or all tasks."""
        try:
            history = self.task_uow.history.get_history(task_id)
            logger.info("Fetched %d history entries", len(history))
            return history

        except DatabaseError as e:
            logger.error("Database error in get_task_history: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.get_task_history")
            raise DomainError("Service failed to fetch history") from e

    def create_task(self, task: Task) -> Task:
        try:
            # Run domain validations
            validation_result = pipelines.task_create_validation_pipeline(task.deadline)
            
            if validation_result.is_err():
                error_msg = validation_result.error or "Validation failed"
                raise DomainValidationError([error_msg])
            
            # Generate ID if not provided (client may omit it)
            if not task.id:
                task.id = str(uuid.uuid4())
            
            # Check for duplicate ID
            existing_task = self.task_uow.tasks.get_task(task.id)
            if existing_task:
                raise ValidationError(f"Task with id {task.id} already exists")
            
            # Add task through repository
            created_task = self.task_uow.tasks.add_task(task)
            
            # Record history
            new_value = asdict(created_task)
            self._record_history(
                entity_id=created_task.id,
                entity_type="task",
                change_type=HistoryType.TASK_CREATED,
                old_value=None,
                new_value=str(new_value)
            )
            
            logger.info("Created task with id %s", task.id)
            return created_task

        except (ValidationError, DomainValidationError):
            raise

        except DatabaseError as e:
            logger.error("Database error in create_task: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.create_task")
            raise DomainError("Service failed to create task") from e

    def update_task(self, task_id: str, task: Task) -> Task:
        try:
            # Check if task exists
            existing_task = self.task_uow.tasks.get_task(task_id)
            if not existing_task:
                logger.warning("Task with id %s not found for update", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            # Run domain validations for update
            # Get the new values from the task being updated
            new_deadline = task.deadline
            new_status = task.status
            
            validation_result = pipelines.task_update_validation_pipeline(
                old_task=existing_task,
                new_deadline=new_deadline,
                new_status=new_status
            )
            
            if validation_result.is_err():
                error_msg = validation_result.error or "Validation failed"
                raise DomainValidationError([error_msg])
            
            # If status is being changed to DONE, validate task completion constraint
            if new_status is not None and new_status != existing_task.status:
                subtasks = self.task_uow.subtasks.get_subtasks(task_id)
                completion_validation = pipelines.task_status_change_pipeline(
                    task=existing_task,
                    new_status=new_status,
                    subtasks=subtasks
                )
                if completion_validation.is_err():
                    error_msg = completion_validation.error or "Validation failed"
                    raise DomainValidationError([error_msg])
            
            # Capture old value for history
            old_value = asdict(existing_task)
            
            # Update the task with the provided ID
            task.id = task_id
            updated_task = self.task_uow.tasks.update_task(task)
            
            # Record history
            new_value = asdict(updated_task)
            self._record_history(
                entity_id=task_id,
                entity_type="task",
                change_type=HistoryType.TASK_UPDATED,
                old_value=str(old_value),
                new_value=str(new_value)
            )
            
            # Cascade status to subtasks if task status is DONE or CANCELLED
            if new_status is not None and new_status != existing_task.status:
                if new_status in (Status.DONE, Status.CANCELLED):
                    self._cascade_status_to_subtasks(
                        task_id=task_id,
                        new_status=new_status
                    )
            
            logger.info("Updated task with id %s", task_id)
            return updated_task

        except (NotFoundError, DomainValidationError):
            raise

        except DatabaseError as e:
            logger.error("Database error in update_task: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.update_task")
            raise DomainError("Service failed to update task") from e

    def _cascade_status_to_subtasks(self, task_id: str, new_status: Status):
        """Cascade status change to all subtasks when task is marked DONE or CANCELLED."""
        subtasks = self.task_uow.subtasks.get_subtasks(task_id)
        
        for subtask in subtasks:
            # Skip if subtask already has the same status
            if subtask.status == new_status:
                continue
            
            # Capture old value for history
            old_value = asdict(subtask)
            
            # Update subtask status
            subtask.status = new_status
            updated_subtask = self.task_uow.subtasks.update_subtask(subtask)
            
            # Record history for subtask
            new_value = asdict(updated_subtask)
            self._record_history(
                entity_id=subtask.id,
                entity_type="subtask",
                change_type=HistoryType.SUBTASK_UPDATED,
                old_value=str(old_value),
                new_value=str(new_value)
            )
            
            logger.info("Cascaded status '%s' to subtask %s (parent task: %s)", 
                       new_status.value, subtask.id, task_id)

    def delete_task(self, task_id: str) -> bool:
        try:
            # Check if task exists
            existing_task = self.task_uow.tasks.get_task(task_id)
            if not existing_task:
                logger.warning("Task with id %s not found for deletion", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            # Capture old value for history before deletion
            old_value = asdict(existing_task)
            
            # Delete the task
            result = self.task_uow.tasks.delete_task(task_id)
            
            # Record history
            self._record_history(
                entity_id=task_id,
                entity_type="task",
                change_type=HistoryType.TASK_DELETED,
                old_value=str(old_value),
                new_value=None
            )
            
            logger.info("Deleted task with id %s", task_id)
            return result

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in delete_task: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.delete_task")
            raise DomainError("Service failed to delete task") from e
