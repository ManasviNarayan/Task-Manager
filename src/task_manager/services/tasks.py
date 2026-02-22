from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.domain.models import Task


class TaskService:

    def __init__(self, task_uow: ITaskUnitOfWork):
        self.task_uow = task_uow

    def get_tasks(self):
        tasks = self.task_uow.tasks.get_tasks()
        return tasks