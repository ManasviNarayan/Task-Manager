# task_manager/api/handlers/tasks.py
from task_manager.api.providers import get_task_list_uow
from task_manager.services.tasks import TaskService
from task_manager.api.schemas import TaskRequestPayload, TaskResponsePayload, UpdateTaskRequestPayload, HistoryResponsePayload
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


def get_history(task_id: str = None) -> tuple[list[dict], int]:
    """Get history entries, optionally filtered by task_id."""
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        history = service.get_task_history(task_id)
        
        history_payload = [
            HistoryResponsePayload.from_domain_model(h).model_dump() 
            for h in history
        ]
        
        logger.info(f"Retrieved {len(history_payload)} history entries")

    return history_payload, HTTPStatus.OK


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


def update_task(task_id: str) -> tuple[dict, int]:
    # Parse and validate request body using UpdateTaskRequestPayload
    # All fields are optional for partial updates
    data = request.get_json()
    update_request = UpdateTaskRequestPayload(**data)
    
    with get_task_list_uow() as uow:
        service = TaskService(uow)
        
        # Get existing task to preserve values for fields not being updated
        existing_task = service.get_task(task_id)
        
        # Convert update request to domain model with existing values
        updated_task_model = update_request.to_domain_model(existing_task)
        
        # Update the task
        updated_task = service.update_task(task_id, updated_task_model)
        logger.info(f"Updated task with id {task_id}")
        
        # Return full response payload with all fields populated
        return TaskResponsePayload.from_domain_model(updated_task).model_dump(), HTTPStatus.OK


def delete_task(task_id: str) -> tuple[dict, int]:
    with get_task_list_uow() as uow:
        service = TaskService(uow)
        
        # Delete the task
        service.delete_task(task_id)
        logger.info(f"Deleted task with id {task_id}")
        
        # Return success message
        return {"message": f"Task with id {task_id} deleted successfully"}, HTTPStatus.NO_CONTENT

