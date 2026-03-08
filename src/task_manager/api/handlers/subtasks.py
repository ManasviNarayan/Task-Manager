"""
API Handlers for subtask operations in the Task Manager application.

This module contains request handlers for subtask-related API endpoints,
including CRUD operations and history retrieval.
"""

import logging
from http import HTTPStatus

from flask import request

from task_manager.api.providers import get_subtask_uow, get_task_list_uow
from task_manager.api.schemas import (
    HistoryResponsePayload,
    SubtaskRequestPayload,
    SubtaskResponsePayload,
    UpdateSubtaskRequestPayload,
)
from task_manager.logger import get_logger
from task_manager.services.subtasks import SubtaskService

logger = get_logger(__name__, logging.INFO)


def get_subtasks(task_id: str) -> tuple[list[dict], int]:
    """
    Get all subtasks for a specific task.

    Args:
        task_id: Unique identifier of the parent task.

    Returns:
        Tuple of (list of subtask dictionaries, HTTP status code).
    """
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        subtasks = [
            SubtaskResponsePayload.from_domain_model(st).model_dump()
            for st in service.get_subtasks(task_id)
        ]

        logger.info(f"Retrieved {len(subtasks)} subtasks for task {task_id}")

    return subtasks, HTTPStatus.OK


def get_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """
    Get a specific subtask by ID.

    Args:
        task_id: Unique identifier of the parent task.
        subtask_id: Unique identifier of the subtask.

    Returns:
        Tuple of (subtask dictionary, HTTP status code).
    """
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        subtask = service.get_subtask(subtask_id)
        logger.info(f"Retrieved subtask with id {subtask_id}")

        return (
            SubtaskResponsePayload.from_domain_model(subtask).model_dump(),
            HTTPStatus.OK,
        )


def create_subtask(task_id: str) -> tuple[dict, int]:
    """
    Create a new subtask for a task.

    Args:
        task_id: Unique identifier of the parent task.

    Returns:
        Tuple of (created subtask dictionary, HTTP status code).
    """
    data = request.get_json()
    subtask_request = SubtaskRequestPayload(**data)
    subtask = subtask_request.to_domain_model(task_id)

    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)
        created_subtask = service.create_subtask(task_id, subtask)

        logger.info(
            f"Created subtask with id {created_subtask.id} for task {task_id}"
        )
        return (
            SubtaskResponsePayload.from_domain_model(created_subtask).model_dump(),
            HTTPStatus.CREATED,
        )


def update_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """
    Update an existing subtask.

    Args:
        task_id: Unique identifier of the parent task.
        subtask_id: Unique identifier of the subtask to update.

    Returns:
        Tuple of (updated subtask dictionary, HTTP status code).
    """
    data = request.get_json()
    update_request = UpdateSubtaskRequestPayload(**data)

    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        existing_subtask = service.get_subtask(subtask_id)
        updated_subtask_model = update_request.to_domain_model(existing_subtask)
        updated_subtask = service.update_subtask(
            subtask_id, updated_subtask_model
        )

        logger.info(f"Updated subtask with id {subtask_id}")
        return (
            SubtaskResponsePayload.from_domain_model(updated_subtask).model_dump(),
            HTTPStatus.OK,
        )


def delete_subtask(task_id: str, subtask_id: str) -> tuple[dict, int]:
    """
    Delete a subtask.

    Args:
        task_id: Unique identifier of the parent task.
        subtask_id: Unique identifier of the subtask to delete.

    Returns:
        Tuple of (success message dictionary, HTTP status code).
    """
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        service.delete_subtask(subtask_id)

        logger.info(f"Deleted subtask with id {subtask_id}")
        return (
            {"message": f"Subtask with id {subtask_id} deleted successfully"},
            HTTPStatus.NO_CONTENT,
        )


def get_subtasks_history(task_id: str) -> tuple[list[dict], int]:
    """
    Get all history entries for a task's subtasks.

    Args:
        task_id: Unique identifier of the parent task.

    Returns:
        Tuple of (list of history dictionaries, HTTP status code).
    """
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        history = service.get_subtasks_history(task_id)

        history_payload = [
            HistoryResponsePayload.from_domain_model(h).model_dump()
            for h in history
        ]

        logger.info(
            f"Retrieved {len(history_payload)} subtask history entries "
            f"for task {task_id}"
        )

    return history_payload, HTTPStatus.OK


def get_subtask_history(task_id: str, subtask_id: str) -> tuple[list[dict], int]:
    """
    Get all history entries for a specific subtask.

    Args:
        task_id: Unique identifier of the parent task.
        subtask_id: Unique identifier of the subtask.

    Returns:
        Tuple of (list of history dictionaries, HTTP status code).
    """
    with get_task_list_uow() as task_uow, get_subtask_uow() as subtask_uow:
        service = SubtaskService(subtask_uow, task_uow)

        history = service.get_subtask_history(subtask_id)

        history_payload = [
            HistoryResponsePayload.from_domain_model(h).model_dump()
            for h in history
        ]

        logger.info(
            f"Retrieved {len(history_payload)} history entries "
            f"for subtask {subtask_id}"
        )

    return history_payload, HTTPStatus.OK

