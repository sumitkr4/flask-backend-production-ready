"""
Pydantic schemas for request/response validation.

WHY Pydantic?
- Validates data at API boundary (prevent bad data early)
- Type hints + runtime validation
- Auto-generates error messages
- Doubles as API documentation
- One place to change validation rules
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


# ============================================================================
# AUTH SCHEMAS - For user registration and login
# ============================================================================

class RegisterSchema(BaseModel):
    """
    Schema for user registration.

    WHY separate fields?
    - name: Required, 1-120 chars (reasonable username length)
    - email: Must be valid email format (EmailStr validates this)
    - password: Minimum 8 chars (basic security requirement)
    """
    name: str = Field(..., min_length=1, max_length=120, description="User's full name")
    email: EmailStr  # Automatically validates email format!
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")

    # WHY validator?
    # - Convert email to lowercase for consistency
    # - Store emails in lowercase (emails are case-insensitive)
    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v):
        return v.lower()


class LoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v):
        return v.lower()


# ============================================================================
# RESPONSE SCHEMAS - What we return to the client
# ============================================================================

class UserResponseSchema(BaseModel):
    """
    User data to return to client.

    WHY?
    - Never expose password hash to client!
    - Only return what client needs
    - This is our contract with frontend
    """
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True  # Convert SQLAlchemy models to Pydantic


class TokenResponseSchema(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="Short-lived access token (15 min)")
    refresh_token: str = Field(..., description="Long-lived refresh token (7 days)")
    token_type: str = Field(default="Bearer", description="Token type is always Bearer")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class AuthResponseSchema(BaseModel):
    """Complete auth response with user and tokens."""
    message: str
    user: UserResponseSchema
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"


class ProfileResponseSchema(BaseModel):
    """Profile response for protected endpoint."""
    message: str
    user: UserResponseSchema


class RefreshTokenSchema(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str = Field(..., description="The refresh token from login")


class ChangePasswordSchema(BaseModel):
    """Schema for changing password."""
    old_password: str = Field(..., min_length=1, description="Current password for verification")
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")


class UpdateProfileSchema(BaseModel):
    """
    Schema for updating user profile.

    WHY Optional fields?
    - User can update just name, just email, or both
    - Flexible partial updates
    """
    name: Optional[str] = Field(None, min_length=1, max_length=120, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")

    @field_validator('email')
    @classmethod
    def lowercase_email(cls, v):
        if v:
            return v.lower()
        return v


# ============================================================================
# WHY CONFIG class?
# ============================================================================
# from_attributes = True allows Pydantic to convert SQLAlchemy models
# Without this, Pydantic can't read SQLAlchemy model attributes
# This is the bridge between database ORM and API responses

# ============================================================================
# WHY CONFIG class?
# ============================================================================
# from_attributes = True allows Pydantic to convert SQLAlchemy models
# Without this, Pydantic can't read SQLAlchemy model attributes
# This is the bridge between database ORM and API responses
