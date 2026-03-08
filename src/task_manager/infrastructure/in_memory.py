# task_manager/infrastructure/in_memory/db.py
from datetime import datetime, timedelta
from task_manager.domain.models import Status, Priority, HistoryType
import uuid

now = datetime.now()
t = now + timedelta(days=1)

# Sample history entries for testing
sample_history = [
    {
        "id": str(uuid.uuid4()),
        "entity_id": "task-001",
        "entity_type": "task",
        "change_type": HistoryType.TASK_CREATED,
        "timestamp": now - timedelta(hours=2),
        "old_value": None,
        "new_value": '{"id": "task-001", "description": "Write initial project scope", "deadline": null, "status": "Todo", "priority": 3}'
    },
    {
        "id": str(uuid.uuid4()),
        "entity_id": "task-001",
        "entity_type": "task",
        "change_type": HistoryType.TASK_UPDATED,
        "timestamp": now - timedelta(hours=1),
        "old_value": '{"status": "Todo"}',
        "new_value": '{"status": "In Progress"}'
    },
    {
        "id": str(uuid.uuid4()),
        "entity_id": "task-002",
        "entity_type": "task",
        "change_type": HistoryType.TASK_CREATED,
        "timestamp": now - timedelta(hours=3),
        "old_value": None,
        "new_value": '{"id": "task-002", "description": "Implement in-memory task repository", "deadline": null, "status": "Todo", "priority": 4}'
    }
]

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
        self.subtasks = [
            {
                "id": "subtask-001",
                "task_id": "task-001",
                "description": "Define business requirements",
                "deadline": t,
                "status": Status.TODO,
            },
            {
                "id": "subtask-002",
                "task_id": "task-001",
                "description": "Define functional requirements",
                "deadline": t,
                "status": Status.IN_PROGRESS,
            },
            {
                "id": "subtask-003",
                "task_id": "task-002",
                "description": "Create repository interface",
                "deadline": t,
                "status": Status.DONE,
            },
        ]
        self.history = sample_history
