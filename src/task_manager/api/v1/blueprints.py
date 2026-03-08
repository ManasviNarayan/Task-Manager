"""
API v1 Blueprint configuration.

This module creates and configures the v1 Blueprint for the Task Manager API,
registering all task and subtask routes.
"""

from flask import Blueprint

from task_manager.api.v1.routes.subtasks import register_subtask_routes
from task_manager.api.v1.routes.tasks import register_task_routes


def get_v1_blueprint() -> Blueprint:
    """
    Create and configure the v1 API Blueprint.

    Registers all task and subtask routes under the /api/v1 URL prefix.

    Returns:
        Configured Flask Blueprint for v1 API.
    """
    v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
    register_task_routes(v1)
    register_subtask_routes(v1)

    return v1

