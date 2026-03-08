# task_manager/domain/models.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class Status(Enum):
    TODO = 'Todo'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'
    CANCELLED = 'Cancelled'
    OVERDUE = 'Overdue'
    
@dataclass
class Task:
    id: Optional[str]
    description: str
    deadline: Optional[datetime]  # Optional - None represents a general task with no deadline
    status: Status
    priority: Priority


@dataclass
class Subtask:
    id: Optional[str]
    task_id: str  # Parent task ID
    description: str
    deadline: Optional[datetime]  # Optional - must not exceed parent task deadline
    status: Status


class HistoryType(Enum):
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    SUBTASK_CREATED = "subtask_created"
    SUBTASK_UPDATED = "subtask_updated"
    SUBTASK_DELETED = "subtask_deleted"


@dataclass
class History:
    id: str
    entity_id: str  # ID of the task or subtask
    entity_type: str  # "task" or "subtask"
    change_type: HistoryType  # What happened
    timestamp: datetime
    old_value: Optional[str]  # JSON serialized old state
    new_value: Optional[str]  # JSON serialized new state

