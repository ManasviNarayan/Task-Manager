# task_manager/api/app.py
from task_manager.api.v1.blueprints import get_v1_blueprint
from task_manager.exceptions import ValidationError, NotFoundError, DomainError, DatabaseError
from http import HTTPStatus
from flask import Flask

def create_app()-> Flask:
    app = Flask(__name__)

    # blueprints
    app.register_blueprint(get_v1_blueprint())

    #   error handlers    
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        response = {"error": "Validation failed", "message": str(err)}
        return response, HTTPStatus.BAD_REQUEST

    @app.errorhandler(NotFoundError)
    def handle_not_found(err):
        response = {"error": "Not Found", "message": str(err)}
        return response, HTTPStatus.NOT_FOUND

    @app.errorhandler(DomainError)
    def handle_domain_error(err):
        response = {"error": "Domain rule violation", "message": str(err)}
        return response, HTTPStatus.CONFLICT
    
    @app.errorhandler(DatabaseError)
    def handle_database_error(err):
        response = {"error": "Database Error", "message": str(err)}
        return response, HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, HTTPStatus.NOT_FOUND

    @app.errorhandler(Exception)
    def handle_generic_error(err):
        response = {"error": "Internal Server Error", "message": str(err)}
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

    return app
