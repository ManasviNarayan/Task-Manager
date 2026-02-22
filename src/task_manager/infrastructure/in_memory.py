# task_manager/infrastructure/in_memory/db.py
from datetime import datetime, timedelta
from task_manager.domain.models import Status, Priority
now = datetime.now()
t = now + timedelta(days=1)

class InMemoryDB:
    """Simple in-memory storage for tasks, subtasks, and history."""
    def __init__(self):
        self.tasks = [    {
        "id": "task-001",
        "description": "Write initial project scope",
        "deadline": t,
        "status": Status.TODO,
        "priority": Priority.HIGH,
    },
    {
        "id": "task-002",
        "description": "Implement in-memory task repository",
        "deadline": t,
        "status": Status.IN_PROGRESS,
        "priority": Priority.CRITICAL,
    },
    {
        "id": "task-003",
        "description": "Decide API versioning strategy",
        "deadline": t,
        "status": Status.DONE,
        "priority": Priority.MEDIUM,
    },
    {
        "id": "task-004",
        "description": "Refactor handler–service boundary",
        "deadline": t,
        "status": Status.OVERDUE,
        "priority": Priority.LOW,
    },]
        self.subtasks = []
        self.history = []
