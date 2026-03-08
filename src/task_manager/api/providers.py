# task_manager/api/providers.py
from task_manager.infrastructure.in_memory import InMemoryDB
from task_manager.data.unit_of_work.in_memory import InMemoryTaskUnitOfWork
from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork

_db = InMemoryDB()  # shared in-memory "session"

def get_task_list_uow() -> ITaskUnitOfWork:
    """Factory function to create Unit of Work instances.
    
    This allows for proper dependency injection while maintaining
    the factory pattern for creating new instances per request.
    """
    return InMemoryTaskUnitOfWork(_db)

