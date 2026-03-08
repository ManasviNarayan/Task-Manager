# task_manager/services/tasks.py
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.domain.models import Task
from task_manager.exceptions import DatabaseError, DomainError, NotFoundError, ValidationError
from task_manager.logger import get_logger
import logging
import uuid

logger = get_logger(__name__, logging.INFO)

class TaskService:

    def __init__(self, task_uow: ITaskUnitOfWork):
        self.task_uow = task_uow

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

    def create_task(self, task: Task) -> Task:
        try:
            # Generate ID if not provided (client may omit it)
            if not task.id:
                task.id = str(uuid.uuid4())
            
            # Check for duplicate ID
            existing_task = self.task_uow.tasks.get_task(task.id)
            if existing_task:
                raise ValidationError(f"Task with id {task.id} already exists")
            
            # Add task through repository
            created_task = self.task_uow.tasks.add_task(task)
            logger.info("Created task with id %s", task.id)
            return created_task

        except ValidationError:
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
            
            # Update the task with the provided ID
            task.id = task_id
            updated_task = self.task_uow.tasks.update_task(task)
            logger.info("Updated task with id %s", task_id)
            return updated_task

        except NotFoundError:
            raise

        except DatabaseError as e:
            logger.error("Database error in update_task: %s", str(e))
            raise

        except Exception as e:
            logger.exception("Unexpected error in TaskService.update_task")
            raise DomainError("Service failed to update task") from e

    def delete_task(self, task_id: str) -> bool:
        try:
            # Check if task exists
            existing_task = self.task_uow.tasks.get_task(task_id)
            if not existing_task:
                logger.warning("Task with id %s not found for deletion", task_id)
                raise NotFoundError(f"Task with id {task_id} not found")
            
            # Delete the task
            result = self.task_uow.tasks.delete_task(task_id)
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
