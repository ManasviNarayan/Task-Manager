from task_manager.api.handlers.tasks import get_tasks
from flask import Blueprint


def register_task_routes(bp: Blueprint):
    bp.add_url_rule(
        '/tasks',
        endpoint='get_tasks',
        view_func=get_tasks,
        methods = ['GET']
    )