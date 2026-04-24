"""Admin routes protected by RBAC."""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.extensions import db
from app.models import User, Role, Permission
from app.utils.permissions import require_permission, require_role
from app.exceptions import ValidationError as ValidationException, NotFoundError


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ============================================================================
# WHY admin endpoints?
# ============================================================================
# Demonstrate RBAC in action
# Show how decorators protect endpoints
# Real-world admin functionality
# ============================================================================


@admin_bp.get("/users")
@require_permission('view_users')
def list_users():
    """
    List all users (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of all users
        schema:
          type: object
          properties:
            message:
              type: string
            users:
              type: array
              items:
                type: object
      403:
        description: Permission denied
    """
    # WHY?
    # - Only users with 'view_users' permission can call this
    # - Decorator checks before this code runs
    users = User.query.all()
    return {
        "message": "Users fetched successfully",
        "users": [u.to_dict() for u in users]
    }, 200



@admin_bp.delete("/users/<int:user_id>")
@require_permission('delete_user')
def delete_user(user_id):
    """
    Delete a user (admin only).
    ---
    tags:
      - Admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: User deleted successfully
      403:
        description: Permission denied
      404:
        description: User not found
    """
    # WHY?
    # - @require_permission('delete_user') ensures only authorized users
    # - Prevents accidental or malicious deletion
    user = User.query.get(user_id)

    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    db.session.delete(user)
    db.session.commit()

    return {
        "message": f"User {user_id} deleted successfully"
    }, 200


@admin_bp.post("/users/<int:user_id>/assign-role/<int:role_id>")
@require_permission('assign_roles')
def assign_role_to_user(user_id, role_id):
    """
    Assign a role to a user (admin only).
    ---
    tags:
      - Admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
      - in: path
        name: role_id
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: Role assigned successfully
      404:
        description: User or role not found
    """
    # WHY?
    # - Only users with 'assign_roles' permission can do this
    # - Prevents privilege escalation
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")

    role = Role.query.get(role_id)
    if not role:
        raise NotFoundError(f"Role {role_id} not found")

    # Check if user already has this role
    if role in user.roles:
        return {
            "message": f"User already has role {role.name}"
        }, 200

    # Assign role
    user.assign_role(role)
    db.session.commit()

    return {
        "message": f"Role {role.name} assigned to user {user.name}",
        "user": user.to_dict(),
        "role": role.to_dict()
    }, 200


@admin_bp.get("/user/<int:user_id>/permissions")
@require_permission('view_users')
def get_user_permissions(user_id):
    """
    Get all permissions for a user (admin only).
    ---
    tags:
      - Admin
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
    security:
      - Bearer: []
    responses:
      200:
        description: User permissions
    """
    # WHY?
    # - Useful for debugging/auditing
    # - See what a user can do
    # - Verify permissions are correct
    user = User.query.get(user_id)

    if not user:
        raise NotFoundError(f"User {user_id} not found")

    return {
        "message": f"Permissions for user {user.name}",
        "user_id": user.id,
        "roles": [r.name for r in user.roles],
        "permissions": user.get_all_permissions()
    }, 200


# ============================================================================
# Protection Summary:
# ============================================================================
# GET    /admin/users                    → @require_permission('view_users')
# DELETE /admin/users/<id>               → @require_permission('delete_user')
# GET    /admin/roles                    → @require_role('admin')
# POST   /admin/users/<id>/assign-role   → @require_permission('assign_roles')
# GET    /admin/user/<id>/permissions    → @require_permission('view_users')
#
# If user doesn't have permission/role → 403 Forbidden
# If user not logged in → 401 Unauthorized
