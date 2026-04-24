"""Test Pydantic schemas validation."""

import pytest
from pydantic import ValidationError

from app.schemas import RegisterSchema, LoginSchema


class TestRegisterSchema:
    """Test RegisterSchema validation."""

    def test_valid_registration(self):
        """Test valid registration data."""
        # WHY test this?
        # - Ensures valid data passes through
        # - Validates Pydantic accepts correct format
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "SecurePass123",
        }
        schema = RegisterSchema(**data)
        assert schema.name == "John Doe"
        assert schema.email == "john@example.com"
        assert schema.password == "SecurePass123"

    def test_invalid_email_format(self):
        """Test invalid email format rejected."""
        # WHY?
        # - Email must be valid format
        # - Pydantic should catch this
        data = {
            "name": "John",
            "email": "invalid-email",  # No @ symbol
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterSchema(**data)

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "email" in str(errors[0])

    def test_password_too_short(self):
        """Test password minimum length."""
        # WHY?
        # - Password must be at least 8 chars
        # - Enforce security requirement
        data = {
            "name": "John",
            "email": "john@example.com",
            "password": "short",  # Less than 8 chars
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterSchema(**data)

        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_missing_name(self):
        """Test missing name field."""
        # WHY?
        # - Name is required
        # - Should fail without it
        data = {
            "email": "john@example.com",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError):
            RegisterSchema(**data)

    def test_missing_email(self):
        """Test missing email field."""
        data = {
            "name": "John",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError):
            RegisterSchema(**data)

    def test_missing_password(self):
        """Test missing password field."""
        data = {
            "name": "John",
            "email": "john@example.com",
        }
        with pytest.raises(ValidationError):
            RegisterSchema(**data)

    def test_empty_name(self):
        """Test empty name rejected."""
        # WHY?
        # - name has min_length=1
        # - Empty string should fail
        data = {
            "name": "",
            "email": "john@example.com",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError):
            RegisterSchema(**data)

    def test_email_lowercase_conversion(self):
        """Test email is converted to lowercase."""
        # WHY?
        # - EmailStr normalizes the value
        data = {
            "name": "John",
            "email": "JOHN@EXAMPLE.COM",
            "password": "SecurePass123",
        }
        schema = RegisterSchema(**data)
        assert schema.email == "john@example.com"


class TestLoginSchema:
    """Test LoginSchema validation."""

    def test_valid_login(self):
        """Test valid login data."""
        data = {
            "email": "john@example.com",
            "password": "SecurePass123",
        }
        schema = LoginSchema(**data)
        assert schema.email == "john@example.com"
        assert schema.password == "SecurePass123"

    def test_invalid_email_format_login(self):
        """Test invalid email in login."""
        data = {
            "email": "invalid-email",
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError):
            LoginSchema(**data)

    def test_missing_email_login(self):
        """Test missing email in login."""
        data = {
            "password": "SecurePass123",
        }
        with pytest.raises(ValidationError):
            LoginSchema(**data)

    def test_missing_password_login(self):
        """Test missing password in login."""
        data = {
            "email": "john@example.com",
        }
        with pytest.raises(ValidationError):
            LoginSchema(**data)

    def test_empty_password_login(self):
        """Test empty password in login."""
        # WHY?
        # - password must have min_length=1
        data = {
            "email": "john@example.com",
            "password": "",
        }
        with pytest.raises(ValidationError):
            LoginSchema(**data)
