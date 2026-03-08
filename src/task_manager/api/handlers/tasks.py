"""
API Handlers for task operations in the Task Manager application.

This module contains request handlers for task-related API endpoints,
including CRUD operations and history retrieval.
"""

import logging
from http import HTTPStatus

from flask import request

from task_manager.api.providers import get_task_list_uow
from task_manager.api.schemas import (
    HistoryResponsePayload,
    TaskRequestPayload,
    TaskResponsePayload,
    UpdateTaskRequestPayload,
)
from task_manager.exceptions import NotFoundError
from task_manager.logger import get_logger
from task_manager.services.tasks import TaskService

logger = get_logger(__name__, logging.INFO)


def get_tasks() -> tuple[list[dict], int]:
    """
    Retrieve all tasks.

    Returns:
        Tuple of (list of task dictionaries, HTTP status code).
    """
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        tasks = [
            TaskResponsePayload.from_domain_model(task).model_dump()
            for task in service.get_tasks()
        ]

        logger.info(f"Retrieved {len(tasks)} tasks")

    return tasks, HTTPStatus.OK


def get_task(task_id: str) -> tuple[dict, int]:
    """
    Retrieve a specific task by its ID.

    Args:
        task_id: Unique identifier of the task.

    Returns:
        Tuple of (task dictionary, HTTP status code).

    Raises:
        NotFoundError: If the task is not found.
    """
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        task = service.get_task(task_id)
        logger.info(f"Retrieved task with id {task_id}")
        return (
            TaskResponsePayload.from_domain_model(task).model_dump(),
            HTTPStatus.OK,
        )


def get_history(task_id: str | None = None) -> tuple[list[dict], int]:
    """
    Get history entries, optionally filtered by task_id.

    Args:
        task_id: Optional filter for specific task.

    Returns:
        Tuple of (list of history dictionaries, HTTP status code).
    """
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
    """
    Create a new task.

    Parses and validates request body using TaskRequestPayload.
    Pydantic will raise ValidationError if invalid.
    Only description is required; other fields have sensible defaults.

    Returns:
        Tuple of (created task dictionary, HTTP status code).
    """
    data = request.get_json()
    task_request = TaskRequestPayload(**data)
    task = task_request.to_domain_model()

    with get_task_list_uow() as uow:
        service = TaskService(uow)
        created_task = service.create_task(task)
        logger.info(f"Created task with id {created_task.id}")

        return (
            TaskResponsePayload.from_domain_model(created_task).model_dump(),
            HTTPStatus.CREATED,
        )


def update_task(task_id: str) -> tuple[dict, int]:
    """
    Update an existing task.

    Parses and validates request body using UpdateTaskRequestPayload.
    All fields are optional for partial updates.

    Args:
        task_id: Unique identifier of the task to update.

    Returns:
        Tuple of (updated task dictionary, HTTP status code).

    Raises:
        NotFoundError: If the task is not found.
    """
    data = request.get_json()
    update_request = UpdateTaskRequestPayload(**data)

    with get_task_list_uow() as uow:
        service = TaskService(uow)

        existing_task = service.get_task(task_id)

        updated_task_model = update_request.to_domain_model(existing_task)

        updated_task = service.update_task(task_id, updated_task_model)
        logger.info(f"Updated task with id {task_id}")

        return (
            TaskResponsePayload.from_domain_model(updated_task).model_dump(),
            HTTPStatus.OK,
        )


def delete_task(task_id: str) -> tuple[dict, int]:
    """
    Delete a task.

    Args:
        task_id: Unique identifier of the task to delete.

    Returns:
        Tuple of (success message dictionary, HTTP status code).

    Raises:
        NotFoundError: If the task is not found.
    """
    with get_task_list_uow() as uow:
        service = TaskService(uow)

        service.delete_task(task_id)
        logger.info(f"Deleted task with id {task_id}")

        return (
            {"message": f"Task with id {task_id} deleted successfully"},
            HTTPStatus.NO_CONTENT,
        )

