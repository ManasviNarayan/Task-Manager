"""
API v1 Route registration for task endpoints.

This module registers all task-related URL rules with the Blueprint.
"""

from flask import Blueprint

from task_manager.api.handlers.tasks import (
    create_task,
    delete_task,
    get_history,
    get_task,
    get_tasks,
    update_task,
)


def register_task_routes(bp: Blueprint) -> None:
    """
    Register all task-related routes with the given Blueprint.

    Args:
        bp: Flask Blueprint to register routes on.
    """
    bp.add_url_rule(
        '/tasks',
        endpoint='get_tasks',
        view_func=get_tasks,
        methods=['GET']
    )

    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='get_task',
        view_func=get_task,
        methods=['GET']
    )

    bp.add_url_rule(
        '/tasks',
        endpoint='create_task',
        view_func=create_task,
        methods=['POST']
    )

    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='update_task',
        view_func=update_task,
        methods=['PUT']
    )

    bp.add_url_rule(
        '/tasks/<task_id>',
        endpoint='delete_task',
        view_func=delete_task,
        methods=['DELETE']
    )

    bp.add_url_rule(
        '/tasks/history',
        endpoint='get_history',
        view_func=get_history,
        methods=['GET']
    )

    bp.add_url_rule(
        '/tasks/history/<task_id>',
        endpoint='get_task_history',
        view_func=get_history,
        methods=['GET']
    )

