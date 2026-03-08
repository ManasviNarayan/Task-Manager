"""
API Schemas for the Task Manager application.

This module contains Pydantic models for request/response validation
and serialization in the API layer.
"""

from dataclasses import asdict
from datetime import datetime

from pydantic import BaseModel, Field
from typing import TYPE_CHECKING, Optional, Type

from task_manager.domain.models import History, HistoryType, Priority, Status, Subtask, Task

if TYPE_CHECKING:
    pass


class TaskRequestPayload(BaseModel):
    """
    Schema for creating a new task.

    Only description is required. Other fields have sensible defaults:
    - deadline: Optional - can be blank for general tasks
    - status: Defaults to TODO
    - priority: Defaults to LOW
    - id: Auto-generated if not provided
    """

    description: str = Field(..., min_length=1)
    deadline: Optional[datetime] = None
    status: Status = Status.TODO
    priority: Priority = Priority.LOW

    model_config = {
        "use_enum_values": True
    }

    def to_domain_model(self) -> Task:
        """
        Convert request payload to domain model.

        Returns:
            Task domain model with the request data.
        """
        return Task(
            id=None,
            description=self.description,
            deadline=self.deadline,
            status=Status(self.status),
            priority=Priority(self.priority)
        )


class TaskResponsePayload(BaseModel):
    """
    Schema for task responses.

    Contains all task fields including:
    - id: The unique identifier
    - description: Task description
    - deadline: Due date (required in response - serialized from optional field)
    - status: Current status
    - priority: Priority level
    """

    id: str
    description: str
    deadline: Optional[datetime]
    status: Status
    priority: Priority

    model_config = {
        "use_enum_values": True
    }

    @classmethod
    def from_domain_model(cls, task: Task) -> "TaskResponsePayload":
        """
        Convert domain model to response payload.

        Args:
            task: Task domain model.

        Returns:
            TaskResponsePayload instance.
        """
        return cls(**asdict(task))


TaskPayload = TaskResponsePayload


class UpdateTaskRequestPayload(BaseModel):
    """
    Schema for updating an existing task.

    All fields are optional to allow partial updates:
    - description: Task description (can be updated)
    - deadline: Due date (can be updated, set to None to remove deadline)
    - status: Current status (can be updated)
    - priority: Priority level (can be updated)
    """

    description: Optional[str] = Field(None, min_length=1)
    deadline: Optional[datetime] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None

    model_config = {
        "use_enum_values": True
    }

    def to_domain_model(self, existing_task: Task) -> Task:
        """
        Convert request payload to domain model, preserving existing
        values for None fields.

        Args:
            existing_task: The existing task to use as base for updates.

        Returns:
            Task domain model with merged data.
        """
        return Task(
            id=existing_task.id,
            description=self.description if self.description is not None else existing_task.description,
            deadline=self.deadline if self.deadline is not None else existing_task.deadline,
            status=Status(self.status) if self.status is not None else existing_task.status,
            priority=Priority(self.priority) if self.priority is not None else existing_task.priority
        )


class HistoryResponsePayload(BaseModel):
    """
    Schema for history responses.

    Contains all history fields including:
    - id: The unique identifier
    - entity_id: ID of the task or subtask
    - entity_type: "task" or "subtask"
    - change_type: What happened (created, updated, deleted)
    - timestamp: When the change occurred
    - old_value: Previous state (JSON string)
    - new_value: New state (JSON string)
    """

    id: str
    entity_id: str
    entity_type: str
    change_type: HistoryType
    timestamp: datetime
    old_value: Optional[str]
    new_value: Optional[str]

    model_config = {
        "use_enum_values": True
    }

    @classmethod
    def from_domain_model(cls, history: History) -> "HistoryResponsePayload":
        """
        Convert domain model to response payload.

        Args:
            history: History domain model.

        Returns:
            HistoryResponsePayload instance.
        """
        return cls(**asdict(history))


class SubtaskRequestPayload(BaseModel):
    """
    Schema for creating a new subtask.

    Only description is required. Other fields have sensible defaults:
    - deadline: Optional - can be blank for general subtasks
    - status: Defaults to TODO
    - task_id: Set by the service layer based on the URL
    - id: Auto-generated if not provided
    """

    description: str = Field(..., min_length=1)
    deadline: Optional[datetime] = None
    status: Status = Status.TODO

    model_config = {
        "use_enum_values": True
    }

    def to_domain_model(self, task_id: str) -> Subtask:
        """
        Convert request payload to domain model.

        Args:
            task_id: ID of the parent task.

        Returns:
            Subtask domain model with the request data.
        """
        return Subtask(
            id=None,
            task_id=task_id,
            description=self.description,
            deadline=self.deadline,
            status=Status(self.status)
        )


class SubtaskResponsePayload(BaseModel):
    """
    Schema for subtask responses.

    Contains all subtask fields including:
    - id: The unique identifier
    - task_id: Parent task ID
    - description: Subtask description
    - deadline: Due date
    - status: Current status
    """

    id: str
    task_id: str
    description: str
    deadline: Optional[datetime]
    status: Status

    model_config = {
        "use_enum_values": True
    }

    @classmethod
    def from_domain_model(cls, subtask: Subtask) -> "SubtaskResponsePayload":
        """
        Convert domain model to response payload.

        Args:
            subtask: Subtask domain model.

        Returns:
            SubtaskResponsePayload instance.
        """
        return cls(**asdict(subtask))


class UpdateSubtaskRequestPayload(BaseModel):
    """
    Schema for updating an existing subtask.

    All fields are optional to allow partial updates:
    - description: Subtask description (can be updated)
    - deadline: Due date (can be updated, set to None to remove deadline)
    - status: Current status (can be updated)
    """

    description: Optional[str] = Field(None, min_length=1)
    deadline: Optional[datetime] = None
    status: Optional[Status] = None

    model_config = {
        "use_enum_values": True
    }

    def to_domain_model(self, existing_subtask: Subtask) -> Subtask:
        """
        Convert request payload to domain model, preserving existing
        values for None fields.

        Args:
            existing_subtask: The existing subtask to use as base for updates.

        Returns:
            Subtask domain model with merged data.
        """
        return Subtask(
            id=existing_subtask.id,
            task_id=existing_subtask.task_id,
            description=self.description if self.description is not None else existing_subtask.description,
            deadline=self.deadline if self.deadline is not None else existing_subtask.deadline,
            status=Status(self.status) if self.status is not None else existing_subtask.status
        )

