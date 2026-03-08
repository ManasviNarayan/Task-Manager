# task_manager/api/v1/routes/tasks.py
from task_manager.api.handlers.tasks import get_tasks, get_task, create_task, update_task, delete_task, get_history
from flask import Blueprint


def register_task_routes(bp: Blueprint):
    bp.add_url_rule(
        '/tasks',
        endpoint='get_tasks',
        view_func=get_tasks,
        methods = ['GET']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='get_task',
        view_func=get_task,
        methods = ['GET']
    )
    
    bp.add_url_rule(
        '/tasks',
        endpoint='create_task',
        view_func=create_task,
        methods = ['POST']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='update_task',
        view_func=update_task,
        methods = ['PUT']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='delete_task',
        view_func=delete_task,
        methods = ['DELETE']
    )
    
    bp.add_url_rule(
        '/tasks/history',
        endpoint='get_history',
        view_func=get_history,
        methods = ['GET']
    )
    
    bp.add_url_rule(
        '/tasks/history/<task_id>',
        endpoint='get_task_history',
        view_func=get_history,
        methods = ['GET']
    )
