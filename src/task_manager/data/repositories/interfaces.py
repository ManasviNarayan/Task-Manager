"""
Repository interfaces for the Task Manager application.

This module defines abstract repository interfaces that define contracts
for data access operations. These interfaces enable dependency inversion
and make the service layer independent of specific storage implementations.
"""

from abc import ABC, abstractmethod
from task_manager.domain.models import Task, Subtask, History


class ITaskRepository(ABC):
    """
    Abstract interface for task data access operations.
    
    Defines the contract for CRUD operations on tasks.
    Implementations can provide different storage backends (in-memory, database, etc.).
    """

    @abstractmethod
    def get_tasks(self) -> list[Task]:
        """
        Retrieve all tasks from storage.
        
        Returns:
            List of all Task objects.
        """
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Task | None:
        """
        Retrieve a specific task by its ID.
        
        Args:
            task_id: Unique identifier of the task.
            
        Returns:
            Task object if found, None otherwise.
        """
        pass

    @abstractmethod
    def add_task(self, task: Task) -> Task:
        """
        Create a new task in storage.
        
        Args:
            task: Task object to create.
            
        Returns:
            The created task with any generated fields (e.g., ID).
        """
        pass

    @abstractmethod
    def update_task(self, task: Task) -> Task | None:
        """
        Update an existing task in storage.
        
        Args:
            task: Task object with updated fields (must include ID).
            
        Returns:
            Updated task if found, None if not found.
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from storage.
        
        Args:
            task_id: Unique identifier of the task to delete.
            
        Returns:
            True if task was deleted, False if not found.
        """
        pass


class ISubtaskRepository(ABC):
    """
    Abstract interface for subtask data access operations.
    
    Defines the contract for CRUD operations on subtasks.
    """

    @abstractmethod
    def get_subtasks(self, task_id: str) -> list[Subtask]:
        """
        Get all subtasks for a specific task.
        
        Args:
            task_id: ID of the parent task.
            
        Returns:
            List of Subtask objects belonging to the task.
        """
        pass

    @abstractmethod
    def get_subtask(self, subtask_id: str) -> Subtask | None:
        """
        Retrieve a specific subtask by its ID.
        
        Args:
            subtask_id: Unique identifier of the subtask.
            
        Returns:
            Subtask object if found, None otherwise.
        """
        pass

    @abstractmethod
    def add_subtask(self, subtask: Subtask) -> Subtask:
        """
        Create a new subtask in storage.
        
        Args:
            subtask: Subtask object to create.
            
        Returns:
            The created subtask with any generated fields.
        """
        pass

    @abstractmethod
    def update_subtask(self, subtask: Subtask) -> Subtask | None:
        """
        Update an existing subtask in storage.
        
        Args:
            subtask: Subtask object with updated fields.
            
        Returns:
            Updated subtask if found, None if not found.
        """
        pass

    @abstractmethod
    def delete_subtask(self, subtask_id: str) -> bool:
        """
        Delete a subtask from storage.
        
        Args:
            subtask_id: Unique identifier of the subtask to delete.
            
        Returns:
            True if subtask was deleted, False if not found.
        """
        pass


class IHistoryRepository(ABC):
    """
    Abstract interface for history/audit log data access operations.
    
    Defines the contract for recording and retrieving history entries
    that track changes to tasks and subtasks.
    """

    @abstractmethod
    def get_history(self, entity_id: str | None = None) -> list[History]:
        """
        Get history entries, optionally filtered by entity ID.
        
        Args:
            entity_id: Optional filter for specific entity. 
                      If None, returns all history entries.
            
        Returns:
            List of History objects, filtered by entity_id if provided.
        """
        pass

    @abstractmethod
    def get_history_for_task_subtasks(self, task_id: str) -> list[History]:
        """
        Get all history entries for a task's subtasks.
        
        This returns subtask-level history only (not task-level history).
        
        Args:
            task_id: ID of the parent task.
            
        Returns:
            List of History entries for subtasks of the task.
        """
        pass

    @abstractmethod
    def get_history_for_subtask(self, subtask_id: str) -> list[History]:
        """
        Get all history entries for a specific subtask.
        
        Args:
            subtask_id: ID of the subtask.
            
        Returns:
            List of History entries for the subtask.
        """
        pass

    @abstractmethod
    def add_history(self, history: History) -> History:
        """
        Add a new history entry to storage.
        
        Args:
            history: History object to create.
            
        Returns:
            The created history entry.
        """
        pass

