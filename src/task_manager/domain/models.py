from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
class TaskModel:
    id : str | None
    description : str
    deadline: datetime
    status: Status
    priority : Priority



