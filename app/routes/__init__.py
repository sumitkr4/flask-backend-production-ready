from flask import Flask

from app.routes.auth_routes import auth_bp
from app.routes.profile_routes import profile_bp
from app.routes.admin_routes import admin_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

