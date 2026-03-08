# task_manager/api/handlers/tasks.py
from task_manager.api.providers import get_task_list_uow
from task_manager.services.tasks import TaskService
from task_manager.api.schemas import TaskRequestPayload, TaskResponsePayload
from task_manager.logger import get_logger
from task_manager.exceptions import NotFoundError
from http import HTTPStatus
from flask import request
import logging

logger = get_logger(__name__, logging.INFO)


def get_tasks() -> tuple[list[dict], int]:
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        tasks = [TaskResponsePayload.from_domain_model(task).model_dump() 
                 for task in service.get_tasks()]
        
        logger.info(f"Retrieved {len(tasks)} tasks")

    return tasks, HTTPStatus.OK


def get_task(task_id: str) -> tuple[dict, int]:
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        task = service.get_task(task_id)
        logger.info(f"Retrieved task with id {task_id}")
        return TaskResponsePayload.from_domain_model(task).model_dump(), HTTPStatus.OK


def create_task() -> tuple[dict, int]:
    # Parse and validate request body using TaskRequestPayload
    # Pydantic will raise ValidationError if invalid
    # Only description is required; other fields have sensible defaults
    data = request.get_json()
    task_request = TaskRequestPayload(**data)
    task = task_request.to_domain_model()
    
    with get_task_list_uow() as uow:
        service = TaskService(uow)
        created_task = service.create_task(task)
        logger.info(f"Created task with id {created_task.id}")
        
        # Return full response payload with all fields populated
        return TaskResponsePayload.from_domain_model(created_task).model_dump(), HTTPStatus.CREATED

