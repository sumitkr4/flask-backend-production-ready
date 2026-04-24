"""Permission decorators for RBAC."""

from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask import jsonify

from app.models import User
from app.exceptions import AuthorizationError


def require_permission(permission_name):
    """
    Decorator to check if user has specific permission.

    WHY?
    - Checks user's roles → permissions
    - Prevents unauthorized access at route level
    - Reusable across all endpoints
    - Clean, readable code

    Usage:
    @app.post("/delete-user/<user_id>")
    @require_permission('delete_user')
    def delete_user(user_id):
        # Only users with 'delete_user' permission reach here
        ...

    How it works:
    1. Verify JWT token exists (via verify_jwt_in_request)
    2. Get current user ID from token
    3. Query user from database
    4. Check if user has the required permission
    5. If YES: Continue to endpoint
    6. If NO: Raise AuthorizationError (403)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT token exists and is valid
            verify_jwt_in_request()

            # Get user ID from JWT token
            user_id = get_jwt_identity()

            # Query user from database
            user = User.query.get(user_id)

            # Check if user exists
            if not user:
                raise AuthorizationError("User not found")

            # Check if user has the required permission
            if not user.has_permission(permission_name):
                raise AuthorizationError(
                    f"You do not have permission: {permission_name}"
                )

            # If all checks pass, call the original function
            return fn(*args, **kwargs)

        return wrapper
    return decorator


def require_role(role_name):
    """
    Decorator to check if user has specific role.

    WHY?
    - Simpler than permission checking
    - For broad access control (e.g., "admin only")
    - More readable for role-level checks

    Usage:
    @app.get("/admin/dashboard")
    @require_role('admin')
    def admin_dashboard():
        # Only admins can access
        return stats()

    How it works:
    1. Verify JWT token exists
    2. Get current user from token
    3. Check if user has the role
    4. If YES: Continue to endpoint
    5. If NO: Raise AuthorizationError (403)
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT token
            verify_jwt_in_request()

            # Get user ID from JWT
            user_id = get_jwt_identity()

            # Query user
            user = User.query.get(user_id)

            if not user:
                raise AuthorizationError("User not found")

            # Check if user has the role
            if not user.has_role(role_name):
                raise AuthorizationError(
                    f"You do not have role: {role_name}"
                )

            # Call original function
            return fn(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# WHY separate decorators?
# ============================================================================
# @require_permission('delete_user')
# - Fine-grained: Can have same permission in multiple roles
# - Example: Both 'admin' and 'moderator' have 'delete_spam'
#
# @require_role('admin')
# - Coarse-grained: Check entire role, not individual permissions
# - Example: Only 'admin' role can access /admin/dashboard
#
# Use @require_permission for specific actions
# Use @require_role for broad admin areas
