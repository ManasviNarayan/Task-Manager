# task_manager/api/handlers/subtasks.py
from task_manager.api.providers import get_task_list_uow, get_subtask_uow
from task_manager.services.subtasks import SubtaskService
from task_manager.api.schemas import SubtaskRequestPayload, SubtaskResponsePayload, UpdateSubtaskRequestPayload, HistoryResponsePayload
from task_manager.logger import get_logger
from http import HTTPStatus
from flask import request
import logging

logger = get_logger(__name__, logging.INFO)


def get_subtasks(task_id: str) -> tuple[list[dict], int]:
    """Get all subtasks for a specific task."""
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        subtasks = [SubtaskResponsePayload.from_domain_model(st).model_dump() 
                   for st in service.get_subtasks(task_id)]
        
        logger.info(f"Retrieved {len(subtasks)} subtasks for task {task_id}")
        
    return subtasks, HTTPStatus.OK


def get_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """Get a specific subtask by ID."""
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        subtask = service.get_subtask(subtask_id)
        logger.info(f"Retrieved subtask with id {subtask_id}")
        
        return SubtaskResponsePayload.from_domain_model(subtask).model_dump(), HTTPStatus.OK


def create_subtask(task_id: str) -> tuple[dict, int]:
    """Create a new subtask for a task."""
    data = request.get_json()
    subtask_request = SubtaskRequestPayload(**data)
    subtask = subtask_request.to_domain_model(task_id)
    
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        created_subtask = service.create_subtask(task_id, subtask)
        
        logger.info(f"Created subtask with id {created_subtask.id} for task {task_id}")
        return SubtaskResponsePayload.from_domain_model(created_subtask).model_dump(), HTTPStatus.CREATED


def update_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """Update an existing subtask."""
    data = request.get_json()
    update_request = UpdateSubtaskRequestPayload(**data)
    
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        existing_subtask = service.get_subtask(subtask_id)
        updated_subtask_model = update_request.to_domain_model(existing_subtask)
        updated_subtask = service.update_subtask(subtask_id, updated_subtask_model)
        
        logger.info(f"Updated subtask with id {subtask_id}")
        return SubtaskResponsePayload.from_domain_model(updated_subtask).model_dump(), HTTPStatus.OK


def delete_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """Delete a subtask."""
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        service.delete_subtask(subtask_id)
        
        logger.info(f"Deleted subtask with id {subtask_id}")
        return {"message": f"Subtask with id {subtask_id} deleted successfully"}, HTTPStatus.NO_CONTENT


def get_subtasks_history(task_id: str) -> tuple[list[dict], int]:
    """Get all history entries for a task's subtasks."""
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        history = service.get_subtasks_history(task_id)
        
        history_payload = [
            HistoryResponsePayload.from_domain_model(h).model_dump() 
            for h in history
        ]
        
        logger.info(f"Retrieved {len(history_payload)} subtask history entries for task {task_id}")
        
    return history_payload, HTTPStatus.OK


def get_subtask_history(task_id: str, subtask_id: str) -> tuple[list[dict], int]:
    """Get all history entries for a specific subtask."""
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        
        history = service.get_subtask_history(subtask_id)
        
        history_payload = [
            HistoryResponsePayload.from_domain_model(h).model_dump() 
            for h in history
        ]
        
        logger.info(f"Retrieved {len(history_payload)} history entries for subtask {subtask_id}")
        
    return history_payload, HTTPStatus.OK

