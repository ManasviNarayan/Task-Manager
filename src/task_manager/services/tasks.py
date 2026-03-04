# task_manager/services/tasks.py
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.domain.models import Task
from task_manager.exceptions import DatabaseError, DomainError, NotFoundError
from task_manager.logger import get_logger
import logging

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
