"""Tests for authentication API endpoints."""

import pytest
import json
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Create app for testing."""
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


class TestRegisterEndpoint:
    """Test POST /auth/register endpoint."""

    def test_register_valid_user(self, client):
        """Test registering a valid user."""
        # WHY?
        # - End-to-end test: request → validation → service → response
        response = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John Doe',
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert data['user']['email'] == 'john@test.com'

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        # WHY?
        # - Pydantic should reject invalid email
        response = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'invalid-email',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'Validation failed' in data['message']

    def test_register_short_password(self, client):
        """Test registration with short password."""
        response = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com',
                'password': 'short'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'Validation failed' in data['message']

    def test_register_missing_field(self, client):
        """Test registration with missing field."""
        response = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com'
                # Missing password
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'Validation failed' in data['message']

    def test_register_duplicate_email(self, client):
        """Test registration fails with duplicate email."""
        # Register first user
        response1 = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com',
                'password': 'Pass123456'  # 10 chars - valid!
            }),
            content_type='application/json'
        )
        print(f"First register: {response1.status_code} - {response1.get_json()}")

        # Try to register with same email
        response = client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'Jane',
                'email': 'john@test.com',
                'password': 'Pass456789'  # 10 chars - valid!
            }),
            content_type='application/json'
        )

        print(f"Second register: {response.status_code} - {response.get_json()}")

        assert response.status_code == 409
        data = response.get_json()
        assert 'already registered' in data['message']


class TestLoginEndpoint:
    """Test POST /auth/login endpoint."""

    def test_login_success(self, client):
        """Test successful login."""
        # Register user
        client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        # Login
        response = client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'john@test.com'

    def test_login_invalid_password(self, client):
        """Test login with wrong password."""
        # Register user
        client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        # Try login with wrong password
        response = client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'john@test.com',
                'password': 'WrongPassword'
            }),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['message']

    def test_login_user_not_found(self, client):
        """Test login with non-existent user."""
        response = client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'nonexistent@test.com',
                'password': 'SomePassword'
            }),
            content_type='application/json'
        )

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['message']

    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format."""
        response = client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'invalid-email',
                'password': 'SomePassword'
            }),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.get_json()
        assert 'Validation failed' in data['message']


class TestProfileEndpoint:
    """Test GET /profile endpoint."""

    def test_profile_with_token(self, client):
        """Test accessing profile with valid token."""
        # Register and login
        client.post(
            '/auth/register',
            data=json.dumps({
                'name': 'John',
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        login_response = client.post(
            '/auth/login',
            data=json.dumps({
                'email': 'john@test.com',
                'password': 'SecurePass123'
            }),
            content_type='application/json'
        )

        token = login_response.get_json()['access_token']

        # Access profile
        response = client.get(
            '/profile',
            headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'john@test.com'

    def test_profile_without_token(self, client):
        """Test accessing profile without token."""
        response = client.get('/profile')

        assert response.status_code == 401

    def test_profile_with_invalid_token(self, client):
        """Test accessing profile with invalid token."""
        response = client.get(
            '/profile',
            headers={'Authorization': 'Bearer invalid-token'}
        )

        assert response.status_code == 422  # Unprocessable Entity (invalid JWT)
