"""
Domain models for the Task Manager application.

This module contains all core business entities represented as dataclasses
and enums. These models are framework-agnostic and contain no dependencies
on persistence, HTTP, or other external concerns.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class Priority(Enum):
    """
    Priority levels for tasks.
    
    Attributes:
        LOW: Low priority tasks
        MEDIUM: Medium priority tasks
        HIGH: High priority tasks
        CRITICAL: Critical priority tasks
    """
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class Status(Enum):
    """
    Status values for tasks and subtasks.
    
    Attributes:
        TODO: Task/Subtask is pending
        IN_PROGRESS: Task/Subtask is actively being worked on
        DONE: Task/Subtask has been completed
        CANCELLED: Task/Subtask was cancelled
        OVERDUE: Task/Subtask has passed its deadline
    """
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELLED = "Cancelled"
    OVERDUE = "Overdue"


@dataclass
class Task:
    """
    Represents a task in the task management system.
    
    Attributes:
        id: Unique identifier for the task (None for new tasks)
        description: Brief description of what needs to be done
        deadline: Due date for the task (None for general tasks)
        status: Current status of the task
        priority: Priority level of the task
    """
    id: Optional[str]
    description: str
    deadline: Optional[datetime]
    status: Status
    priority: Priority


@dataclass
class Subtask:
    """
    Represents a subtask associated with a parent task.
    
    Attributes:
        id: Unique identifier for the subtask (None for new subtasks)
        task_id: ID of the parent task this subtask belongs to
        description: Brief description of the subtask
        deadline: Due date for the subtask (None if not applicable)
        status: Current status of the subtask
    """
    id: Optional[str]
    task_id: str
    description: str
    deadline: Optional[datetime]
    status: Status


class HistoryType(Enum):
    """
    Types of changes that can be recorded in history.
    
    Attributes:
        TASK_CREATED: A new task was created
        TASK_UPDATED: An existing task was modified
        TASK_DELETED: A task was deleted
        SUBTASK_CREATED: A new subtask was created
        SUBTASK_UPDATED: An existing subtask was modified
        SUBTASK_DELETED: A subtask was deleted
    """
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    SUBTASK_CREATED = "subtask_created"
    SUBTASK_UPDATED = "subtask_updated"
    SUBTASK_DELETED = "subtask_deleted"


@dataclass
class History:
    """
    Records a change made to a task or subtask.
    
    This provides an audit trail of all modifications to tasks
    and subtasks within the system.
    
    Attributes:
        id: Unique identifier for this history entry
        entity_id: ID of the task or subtask that was changed
        entity_type: Type of entity ("task" or "subtask")
        change_type: What type of change occurred
        timestamp: When the change occurred
        old_value: Previous state as JSON string (None for creates)
        new_value: New state as JSON string (None for deletes)
    """
    id: str
    entity_id: str
    entity_type: str
    change_type: HistoryType
    timestamp: datetime
    old_value: Optional[str]
    new_value: Optional[str]

