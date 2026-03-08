"""
In-memory database implementation for the Task Manager application.

This module provides a simple in-memory storage for tasks, subtasks,
and history. It is primarily used for development and testing.
"""

from datetime import datetime, timedelta

from task_manager.domain.models import HistoryType, Priority, Status


class InMemoryDB:
    """
    Simple in-memory storage for tasks, subtasks, and history.

    This class provides a shared in-memory database instance that
    persists data during the application runtime. It is primarily
    used for development and testing purposes.
    """

    def __init__(self) -> None:
        """
        Initialize the in-memory database with sample data.
        """
        now = datetime.now()
        t = now + timedelta(days=1)

        self.tasks = [
            {
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
                "description": "Refactor handler-service boundary",
                "deadline": t,
                "status": Status.OVERDUE,
                "priority": Priority.LOW,
            },
        ]

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

        # Sample history entries for testing
        self.history = [
            {
                "id": "history-001",
                "entity_id": "task-001",
                "entity_type": "task",
                "change_type": HistoryType.TASK_CREATED,
                "timestamp": now - timedelta(hours=2),
                "old_value": None,
                "new_value": '{"id": "task-001", "description": "Write initial '
                'project scope", "deadline": null, "status": "Todo", '
                '"priority": 3}',
            },
            {
                "id": "history-002",
                "entity_id": "task-001",
                "entity_type": "task",
                "change_type": HistoryType.TASK_UPDATED,
                "timestamp": now - timedelta(hours=1),
                "old_value": '{"status": "Todo"}',
                "new_value": '{"status": "In Progress"}',
            },
            {
                "id": "history-003",
                "entity_id": "task-002",
                "entity_type": "task",
                "change_type": HistoryType.TASK_CREATED,
                "timestamp": now - timedelta(hours=3),
                "old_value": None,
                "new_value": '{"id": "task-002", "description": "Implement '
                'in-memory task repository", "deadline": null, '
                '"status": "Todo", "priority": 4}',
            },
        ]

