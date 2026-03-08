# task_manager/data//in_memory/task_uow.py

from task_manager.data.repositories.in_memory import InMemoryTaskRepository, InMemorySubtaskRepository, InMemoryHistoryRepository
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork, ISubtaskUnitOfWork
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
import logging

logger = get_logger(__name__, level=logging.INFO)

class InMemoryTaskUnitOfWork(ITaskUnitOfWork):
    def __init__(self, db):
        self._db = db
        self._tasks = InMemoryTaskRepository(db)
        self._subtasks = InMemorySubtaskRepository(db)
        self._history = InMemoryHistoryRepository(db)

    @property
    def tasks(self)-> InMemoryTaskRepository:
        return self._tasks

    @property
    def subtasks(self) -> InMemorySubtaskRepository:
        return self._subtasks

    @property
    def history(self) -> InMemoryHistoryRepository:
        return self._history

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
            logger.error("Transaction rolled back due to exception: %s", exc_val)
        else:
            self.commit()
        return None

    def commit(self):
        try:
            # In-memory has no real transaction, but logger the intent
            logger.debug("Committing transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Commit failed in InMemoryTaskUnitOfWork")
            raise DatabaseError("Commit failed in in-memory UoW") from e

    def rollback(self):
        try:
            logger.debug("Rolling back transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Rollback failed in InMemoryTaskUnitOfWork")
            raise DatabaseError("Rollback failed in in-memory UoW") from e


class InMemorySubtaskUnitOfWork(InMemoryTaskUnitOfWork):
    """Unit of Work for subtask operations that inherits from TaskUnitOfWork.
    
    Inherits all properties (tasks, subtasks, history) from InMemoryTaskUnitOfWork.
    On commit/rollback, it automatically commits/rollbacks the parent class
    for atomic cross-UoW transactions.
    """
    def __init__(self, db):
        super().__init__(db)

    def commit(self):
        try:
            # Commit parent (InMemoryTaskUnitOfWork) first, then self
            super().commit()
            logger.debug("Committing subtask transaction (in-memory no-op)")
        except Exception as e:
            self.rollback()  # Rollback on failure to maintain atomicity
            logger.exception("Commit failed in InMemorySubtaskUnitOfWork")
            raise DatabaseError("Commit failed in in-memory subtask UoW") from e

    def rollback(self):
        try:
            # Rollback parent (InMemoryTaskUnitOfWork) first, then self
            super().rollback()
            logger.debug("Rolling back subtask transaction (in-memory no-op)")
        except Exception as e:
            logger.exception("Rollback failed in InMemorySubtaskUnitOfWork")
            raise DatabaseError("Rollback failed in in-memory subtask UoW") from e
