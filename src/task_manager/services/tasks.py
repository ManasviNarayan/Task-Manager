from task_manager.data.unit_of_work.interfaces import ITaskUnitOfWork
from task_manager.domain.models import TaskModel


class TaskService:

    def __init__(self, task_uow: ITaskUnitOfWork):
        self.task_uow = task_uow

    def get_tasks(self):
        tasks = [TaskModel(**task) for task in  self.task_uow.tasks.fetch_all_tasks()]
        return tasks