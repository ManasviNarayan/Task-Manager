from task_manager.api.v1.blueprints import get_v1_blueprint
from flask import Flask

def create_app():
    app = Flask(__name__)

    app.register_blueprint(get_v1_blueprint())

    return app
