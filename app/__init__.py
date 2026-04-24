from dotenv import load_dotenv
from flask import Flask, jsonify
from flasgger import Swagger

from app.config import config_by_name
from app.extensions import initialize_extensions
from app.routes import register_blueprints
from app.exceptions import AppException


def create_app(config_name: str | None = None) -> Flask:
    # Factory Pattern: this function creates and configures Flask app instances.
    load_dotenv()

    app = Flask(__name__)

    selected_config = config_name or "development"
    app.config.from_object(config_by_name[selected_config])

    initialize_extensions(app)
    register_blueprints(app)
    register_error_handlers(app)

    # ============================================================================
    # WHY this Swagger configuration?
    # ============================================================================
    # securityDefinitions: Tells Swagger about Bearer token authentication
    # This adds the "Authorize" button to the UI
    # Type "apiKey" with name "Authorization" = Bearer token
    # in: "header" = token goes in HTTP header
    # ============================================================================
    swagger = Swagger(
        app,
        template={
            "swagger": "2.0",
            "info": {
                "title": "Flask Production-Ready Backend",
                "description": "JWT Auth + RBAC + Refresh Tokens",
                "version": "1.0.0",
            },
            "host": "localhost:5000",
            "schemes": ["http"],
            # ========================================================================
            # SECURITY DEFINITIONS - THIS IS WHAT CREATES THE AUTHORIZE BUTTON
            # ========================================================================
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
                }
            },
            "security": [
                {"Bearer": []}
            ],
        }
    )

    return app


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppException)
    def handle_app_exception(error):
        """Handle custom AppException and subclasses."""
        # WHY?
        # - AuthorizationError → 403
        # - AuthenticationError → 401
        # - ValidationError → 400
        # - ConflictError → 409
        # - NotFoundError → 404
        response = {
            "message": error.message,
            "error_code": error.error_code,
        }
        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"message": "Bad request", "error": str(error)}), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({"message": "Unauthorized", "error": str(error)}), 401

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({"message": "Forbidden", "error": str(error)}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"message": "Resource not found", "error": str(error)}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"message": "Internal server error", "error": str(error)}), 500


