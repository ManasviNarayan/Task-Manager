# task_manager/api/providers.py
from task_manager.infrastructure.in_memory import InMemoryDB
from task_manager.data.unit_of_work.in_memory import InMemoryTaskUnitOfWork

_db = InMemoryDB()  # shared in-memory “session”

def get_task_list_uow() -> InMemoryTaskUnitOfWork:
    return InMemoryTaskUnitOfWork(_db)
