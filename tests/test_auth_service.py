"""Tests for authentication service."""

import pytest
from app import create_app
from app.extensions import db
from app.models import User
from app.services.auth_service import AuthService


@pytest.fixture
def app():
    """Create app for testing."""
    # WHY fixture?
    # - Setup/teardown for each test
    # - Fresh database for each test
    # - Isolated tests
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestAuthService:
    """Test AuthService business logic."""

    def test_register_user_success(self, app):
        """Test successful user registration."""
        # WHY?
        # - User can register with valid data
        # - User saved to database
        # - Password is hashed
        with app.app_context():
            result, status = AuthService.register_user(
                name="John Doe",
                email="john@test.com",
                password="SecurePass123",
            )

            assert status == 201
            assert result["message"] == "User registered successfully"
            assert result["user"]["name"] == "John Doe"
            assert result["user"]["email"] == "john@test.com"

            # Verify user in database
            user = User.query.filter_by(email="john@test.com").first()
            assert user is not None
            assert user.name == "John Doe"

    def test_register_duplicate_email(self, app):
        """Test registration fails with duplicate email."""
        # WHY?
        # - Email must be unique
        # - Second registration should fail
        with app.app_context():
            # Register first user
            AuthService.register_user(
                name="John",
                email="john@test.com",
                password="Pass123",
            )

            # Try to register with same email
            result, status = AuthService.register_user(
                name="Jane",
                email="john@test.com",
                password="Pass456",
            )

            assert status == 409
            assert "already registered" in result["message"]

    def test_login_success(self, app):
        """Test successful login."""
        # WHY?
        # - User can login with correct credentials
        # - JWT token returned
        with app.app_context():
            # Register user first
            AuthService.register_user(
                name="John",
                email="john@test.com",
                password="SecurePass123",
            )

            # Now login
            result, status = AuthService.login_user(
                email="john@test.com",
                password="SecurePass123",
            )

            assert status == 200
            assert result["message"] == "Login successful"
            assert "access_token" in result
            assert result["user"]["email"] == "john@test.com"

    def test_login_invalid_password(self, app):
        """Test login fails with wrong password."""
        # WHY?
        # - Wrong password should be rejected
        # - Security check
        with app.app_context():
            # Register user
            AuthService.register_user(
                name="John",
                email="john@test.com",
                password="SecurePass123",
            )

            # Try login with wrong password
            result, status = AuthService.login_user(
                email="john@test.com",
                password="WrongPassword",
            )

            assert status == 401
            assert "Invalid credentials" in result["message"]

    def test_login_user_not_found(self, app):
        """Test login fails when user doesn't exist."""
        # WHY?
        # - Non-existent user should fail
        # - Security: don't leak if email exists
        with app.app_context():
            result, status = AuthService.login_user(
                email="nonexistent@test.com",
                password="SomePassword",
            )

            assert status == 401
            assert "Invalid credentials" in result["message"]

    def test_password_is_hashed(self, app):
        """Test password is hashed, not stored in plain text."""
        # WHY?
        # - Security: passwords must be hashed
        # - Password should not equal hash
        with app.app_context():
            AuthService.register_user(
                name="John",
                email="john@test.com",
                password="SecurePass123",
            )

            user = User.query.filter_by(email="john@test.com").first()

            # Password hash should not equal plain password
            assert user.password != "SecurePass123"
            assert user.password.startswith("$2b$")  # bcrypt format

    def test_password_verification_works(self, app):
        """Test password verification with bcrypt."""
        # WHY?
        # - check_password should return True for correct password
        # - Should return False for wrong password
        with app.app_context():
            AuthService.register_user(
                name="John",
                email="john@test.com",
                password="SecurePass123",
            )

            user = User.query.filter_by(email="john@test.com").first()

            # Correct password
            assert user.check_password("SecurePass123") is True

            # Wrong password
            assert user.check_password("WrongPassword") is False
