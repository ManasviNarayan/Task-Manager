# task_manager/domain/models.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class Priority(Enum):
    LOW = 'Low'
    MEDIUM = 'Medium'
    HIGH = 'High'
    CRITICAL = 'Critical'

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

