# task_manager/data//in_memory/task_uow.py

from task_manager.data.repositories.in_memory import InMemoryTaskRepository
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.logger import get_logger
from task_manager.exceptions import DatabaseError
import logging

logger = get_logger(__name__, level=logging.INFO)

class InMemoryTaskUnitOfWork(ITaskUnitOfWork):
    def __init__(self, db):
        self._db = db
        self._tasks = InMemoryTaskRepository(db)

    @property
    def tasks(self)-> InMemoryTaskRepository:
        return self._tasks

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
