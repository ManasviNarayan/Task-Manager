# task_manager/api/v1/blueprints.py
from .routes.tasks import register_task_routes
from .routes.subtasks import register_subtask_routes
from flask import Blueprint

def get_v1_blueprint():
    v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
    register_task_routes(v1)
    register_subtask_routes(v1)

    return v1
