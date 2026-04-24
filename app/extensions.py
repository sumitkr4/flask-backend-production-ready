from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class ExtensionFactory:
    # Creational Pattern: a single place that creates extension instances.
    @staticmethod
    def create_db() -> SQLAlchemy:
        return SQLAlchemy()

    @staticmethod
    def create_migrate() -> Migrate:
        return Migrate()

    @staticmethod
    def create_bcrypt() -> Bcrypt:
        return Bcrypt()

    @staticmethod
    def create_jwt() -> JWTManager:
        return JWTManager()


db = ExtensionFactory.create_db()
migrate = ExtensionFactory.create_migrate()
bcrypt = ExtensionFactory.create_bcrypt()
jwt = ExtensionFactory.create_jwt()


def initialize_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
