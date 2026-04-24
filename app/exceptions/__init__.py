"""
Custom exceptions for the application.

WHY custom exceptions?
- Each exception type = different error scenario
- Catches can be specific: except AuthenticationError instead of Exception
- Better error messages and debugging
- Easy to add error codes for API responses
"""


class AppException(Exception):
    """
    Base exception for all application errors.

    WHY base class?
    - All custom exceptions inherit from this
    - Easy to catch all app errors: except AppException
    - Can add common functionality here (error codes, logging)
    """
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        super().__init__(self.message)


class AuthenticationError(AppException):
    """
    Raised when user authentication fails.

    Examples:
    - Wrong password
    - Invalid credentials
    - Email not found
    """
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """
    Raised when user lacks permission for action.

    WHY different from AuthenticationError?
    - Authentication: "Are you who you say you are?"
    - Authorization: "Are you allowed to do this?"

    Examples:
    - User tries to delete someone else's post
    - User without admin role tries /admin/users endpoint
    """
    def __init__(self, message: str = "You do not have permission for this action"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")


class ValidationError(AppException):
    """
    Raised when input validation fails.

    Examples:
    - Missing required field
    - Invalid email format
    - Password too short
    """
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")


class ConflictError(AppException):
    """
    Raised when resource already exists or state conflict.

    Examples:
    - Email already registered
    - Username taken
    - Record already exists
    """
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409, error_code="CONFLICT_ERROR")


class NotFoundError(AppException):
    """
    Raised when resource not found.

    Examples:
    - User doesn't exist
    - Post not found
    """
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND_ERROR")


class TokenError(AppException):
    """
    Raised for token-related errors.

    Examples:
    - Invalid refresh token
    - Token expired (custom handling, not JWT's default)
    - Token revoked
    """
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, status_code=401, error_code="TOKEN_ERROR")


# WHY separate exceptions?
# 1. Specific catching: except AuthenticationError vs except Exception
# 2. Different HTTP status codes (401 vs 403 vs 409)
# 3. Custom error codes for frontend
# 4. Proper semantic meaning (Auth vs Authz)
# 5. Easy to add logging/monitoring per exception type
