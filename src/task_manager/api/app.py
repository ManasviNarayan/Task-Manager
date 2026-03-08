"""
Flask application factory for the Task Manager API.

This module provides the create_app function which configures
the Flask application with blueprints and error handlers.
"""

from http import HTTPStatus

from flask import Flask
from pydantic import ValidationError as PydanticValidationError

from task_manager.api.v1.blueprints import get_v1_blueprint
from task_manager.exceptions import (
    DatabaseError,
    DomainError,
    DomainValidationError,
    NotFoundError,
    ValidationError,
)


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Sets up:
    - API v1 Blueprint with all routes
    - Error handlers for various exception types

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(get_v1_blueprint())

    # Error handlers

    @app.errorhandler(PydanticValidationError)
    def handle_pydantic_validation_error(err: PydanticValidationError):
        """
        Handle Pydantic validation errors from request payloads.

        Args:
            err: The Pydantic validation exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Validation failed", "message": str(err)}
        return response, HTTPStatus.BAD_REQUEST

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        """
        Handle validation errors from the application.

        Args:
            err: The validation exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Validation failed", "message": str(err)}
        return response, HTTPStatus.BAD_REQUEST

    @app.errorhandler(NotFoundError)
    def handle_not_found(err: NotFoundError):
        """
        Handle NotFoundError exceptions.

        Args:
            err: The not found exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Not Found", "message": str(err)}
        return response, HTTPStatus.NOT_FOUND

    @app.errorhandler(DomainValidationError)
    def handle_domain_validation_error(err: DomainValidationError):
        """
        Handle domain validation errors with multiple error messages.

        Args:
            err: The domain validation exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {
            "error": "Domain validation failed",
            "message": "Multiple validation errors occurred",
            "errors": err.errors
        }
        return response, HTTPStatus.BAD_REQUEST

    @app.errorhandler(DomainError)
    def handle_domain_error(err: DomainError):
        """
        Handle general domain/business rule violations.

        Args:
            err: The domain exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Domain rule violation", "message": str(err)}
        return response, HTTPStatus.CONFLICT

    @app.errorhandler(DatabaseError)
    def handle_database_error(err: DatabaseError):
        """
        Handle database-related errors.

        Args:
            err: The database exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Database Error", "message": str(err)}
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 Not Found errors for unmatched routes.

        Args:
            error: The werkzeug NotFound exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        return {"error": "Not found"}, HTTPStatus.NOT_FOUND

    @app.errorhandler(Exception)
    def handle_generic_error(err: Exception):
        """
        Handle all unhandled exceptions.

        Args:
            err: The unhandled exception.

        Returns:
            Tuple of (error response dict, HTTP status code).
        """
        response = {"error": "Internal Server Error", "message": str(err)}
        return response, HTTPStatus.INTERNAL_SERVER_ERROR

    return app

