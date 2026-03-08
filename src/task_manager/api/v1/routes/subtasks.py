# task_manager/api/v1/routes/subtasks.py
from task_manager.api.handlers.subtasks import (
    get_subtasks,
    get_subtask,
    create_subtask,
    update_subtask,
    delete_subtask,
    get_subtasks_history,
    get_subtask_history
)
from flask import Blueprint


def register_subtask_routes(bp: Blueprint):
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks',
        endpoint='get_subtasks',
        view_func=get_subtasks,
        methods=['GET']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks/<subtask_id>',
        endpoint='get_subtask',
        view_func=get_subtask,
        methods=['GET']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks',
        endpoint='create_subtask',
        view_func=create_subtask,
        methods=['POST']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks/<subtask_id>',
        endpoint='update_subtask',
        view_func=update_subtask,
        methods=['PUT']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks/<subtask_id>',
        endpoint='delete_subtask',
        view_func=delete_subtask,
        methods=['DELETE']
    )
    
    # History endpoints
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks/history',
        endpoint='get_subtasks_history',
        view_func=get_subtasks_history,
        methods=['GET']
    )
    
    bp.add_url_rule(
        '/tasks/<task_id>/subtasks/history/<subtask_id>',
        endpoint='get_subtask_history',
        view_func=get_subtask_history,
        methods=['GET']
    )

