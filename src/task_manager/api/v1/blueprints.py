from .routes.tasks import register_task_routes
from flask import Blueprint

def get_v1_blueprint():
    v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
    register_task_routes(v1)

    return v1
