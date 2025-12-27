# task_manager/api/handlers/tasks.py
from task_manager.api.providers import get_task_list_uow
from task_manager.services.tasks import TaskService
from task_manager.api.schemas import TaskSchema
from http import HTTPStatus

def get_tasks():
    uow = get_task_list_uow()
    service = TaskService(uow)

    tasks = [TaskSchema(**task.__dict__).model_dump() for task in service.get_tasks()]

    return tasks, HTTPStatus.OK
