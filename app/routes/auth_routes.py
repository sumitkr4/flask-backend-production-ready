from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from app.services.auth_service import AuthService
from app.schemas.auth_schemas import (
    RegisterSchema,
    LoginSchema,
    RefreshTokenSchema,
    ChangePasswordSchema,
    UpdateProfileSchema,
    AuthResponseSchema,
)
from app.exceptions import TokenError, AuthenticationError


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ============================================================================
# WHY use Pydantic in routes?
# ============================================================================
# Request validation at the boundary (before processing)
# - Catches bad data early
# - Provides consistent error messages
# - Prevents invalid data from reaching services
# - Self-documents API requirements
# ============================================================================


def validate_schema(schema_class, data):
    """
    Helper function to validate data with Pydantic schema.

    WHY?
    - DRY: Use same validation logic for all endpoints
    - Consistent error handling
    - Can add custom logic here later

    Returns: (validated_data_or_none, error_response_or_none, status_code_or_none)
    """
    try:
        validated = schema_class(**data)
        return validated, None, None
    except ValidationError as e:
        # Convert Pydantic errors to dict format
        errors = e.errors()
        error_messages = [f"{err['loc'][0]}: {err['msg']}" for err in errors]
        error_response = {
            "message": "Validation failed",
            "errors": error_messages,
        }
        return None, error_response, 400


@auth_bp.post("/register")
def register():
    """
    User registration endpoint.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: "John Doe"
              description: "User's full name"
            email:
              type: string
              example: "john@example.com"
              description: "Valid email address"
            password:
              type: string
              example: "SecurePass123"
              description: "Password (minimum 8 characters)"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
            user:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                email:
                  type: string
      400:
        description: Validation failed
        schema:
          type: object
          properties:
            message:
              type: string
            errors:
              type: array
              items:
                type: string
      409:
        description: Email already registered
        schema:
          type: object
          properties:
            message:
              type: string
    """
    # Get JSON data
    payload = request.get_json(silent=True) or {}

    # Validate with Pydantic schema
    validated, error_response, status_code = validate_schema(RegisterSchema, payload)

    if error_response:
        return error_response, status_code

    # Call service with validated data
    # WHY pass .dict()?
    # - Converts Pydantic model to dict for service
    # - Service doesn't need to know about Pydantic
    result, status_code = AuthService.register_user(
        name=validated.name,
        email=validated.email,
        password=validated.password,
    )

    return result, status_code


@auth_bp.post("/login")
def login():
    """
    User login endpoint - returns JWT tokens.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "john@example.com"
            password:
              type: string
              example: "SecurePass123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Login successful"
            user:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                email:
                  type: string
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Validation failed
        schema:
          type: object
          properties:
            message:
              type: string
            errors:
              type: array
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
    """
    # Get JSON data
    payload = request.get_json(silent=True) or {}

    # Validate with Pydantic schema
    validated, error_response, status_code = validate_schema(LoginSchema, payload)

    if error_response:
        return error_response, status_code

    # Call service with validated data
    result, status_code = AuthService.login_user(
        email=validated.email,
        password=validated.password,
    )

    return result, status_code


@auth_bp.post("/refresh")
def refresh():
    """
    Refresh access token using refresh token.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              description: "Refresh token from login response"
    responses:
      200:
        description: New access token generated
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Token refreshed successfully"
            access_token:
              type: string
              description: "New access token (valid 15 min)"
            refresh_token:
              type: string
              description: "New refresh token (rotated)"
            user:
              type: object
      401:
        description: Invalid or expired refresh token
        schema:
          type: object
          properties:
            message:
              type: string
    """
    # Get JSON data
    payload = request.get_json(silent=True) or {}

    # Validate with Pydantic schema
    validated, error_response, status_code = validate_schema(RefreshTokenSchema, payload)

    if error_response:
        return error_response, status_code

    # Call service to refresh token
    try:
        result, status_code = AuthService.refresh_access_token(validated.refresh_token)
        return result, status_code
    except TokenError as e:
        return {"message": e.message, "error_code": e.error_code}, e.status_code


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    Logout user by revoking refresh tokens.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Logout successful"
      401:
        description: Missing or invalid JWT token
    """
    # WHY @jwt_required()?
    # - Get user ID from JWT token
    # - Verify user is authenticated
    # - Revoke their refresh tokens

    user_id = get_jwt_identity()

    result, status_code = AuthService.logout_user(int(user_id))

    return result, status_code


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    """
    Change user password.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
              description: "Current password for verification"
            new_password:
              type: string
              description: "New password (minimum 8 characters)"
    responses:
      200:
        description: Password changed successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Incorrect password or missing JWT
    """
    # WHY @jwt_required()?
    # - Get user ID from JWT
    # - Ensure user is authenticated
    # - Then verify old password matches

    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    # Validate with Pydantic schema
    validated, error_response, status_code = validate_schema(ChangePasswordSchema, payload)

    if error_response:
        return error_response, status_code

    # Call service to change password
    try:
        result, status_code = AuthService.change_password(
            user_id=int(user_id),
            old_password=validated.old_password,
            new_password=validated.new_password
        )
        return result, status_code
    except AuthenticationError as e:
        return {"message": e.message, "error_code": e.error_code}, e.status_code


@auth_bp.put("/profile")
@jwt_required()
def update_profile():
    """
    Update user profile (name and/or email).
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            name:
              type: string
              description: "User's name (optional)"
            email:
              type: string
              description: "User's email (optional)"
    responses:
      200:
        description: Profile updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              type: object
      400:
        description: Validation error
      401:
        description: Missing or invalid JWT token
      409:
        description: Email already in use
    """
    # WHY @jwt_required()?
    # - Get user ID from JWT
    # - Ensure only authenticated users can update their profile
    # - Optional fields: can update name, email, or both

    user_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    # Validate with Pydantic schema
    validated, error_response, status_code = validate_schema(UpdateProfileSchema, payload)

    if error_response:
        return error_response, status_code

    # Call service to update profile
    try:
        result, status_code = AuthService.update_profile(
            user_id=int(user_id),
            name=validated.name,
            email=validated.email
        )
        return result, status_code
    except AuthenticationError as e:
        return {"message": e.message, "error_code": e.error_code}, e.status_code

