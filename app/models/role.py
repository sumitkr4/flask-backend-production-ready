"""
Role and Permission models for RBAC (Role-Based Access Control).

WHY separate models?
- Role: What a user is (admin, user, moderator)
- Permission: What they can do (delete_user, edit_post, view_reports)
- Relationship: admin role has [delete_user, edit_post] permissions

This separation = flexibility:
- Add new role without changing code
- Add new permission without changing code
- Change permissions per role instantly
"""

from app.extensions import db


# ============================================================================
# Association Tables (Many-to-Many relationships)
# ============================================================================
# WHY association tables?
# - User can have multiple Roles
# - Role can have multiple Permissions
# - Django has Built-in through tables, SQLAlchemy needs explicit tables

user_roles = db.Table(
    'user_roles',  # Table name
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
)

role_permissions = db.Table(
    'role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'), primary_key=True),
)


# ============================================================================
# Role Model
# ============================================================================

class Role(db.Model):
    """
    Role model for RBAC.

    Examples:
    - id=1, name='admin'
    - id=2, name='user'
    - id=3, name='moderator'
    """
    __tablename__ = 'roles'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description: str | None = db.Column(db.String(255))

    # Relationships
    # WHY these relationships?
    # - From Role, find all Permissions easily: role.permissions
    # - From Role, find all Users easily: role.users
    permissions = db.relationship(
        'Permission',
        secondary=role_permissions,
        backref=db.backref('roles', lazy='dynamic')
    )

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Role {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': [p.name for p in self.permissions]
        }


# ============================================================================
# Permission Model
# ============================================================================

class Permission(db.Model):
    """
    Permission model for RBAC.

    Examples:
    - name='delete_user'
    - name='edit_post'
    - name='view_reports'

    WHY separate from Role?
    - Same permission can be in multiple roles
    - Easy to audit what permissions exist
    - Easy to revoke permission from all roles at once
    """
    __tablename__ = 'permissions'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description: str | None = db.Column(db.String(255))

    def __init__(self, name: str, description: str | None = None) -> None:
        self.name = name
        self.description = description

    def __repr__(self):
        return f'<Permission {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


# ============================================================================
# WHY this structure?
# ============================================================================
# Table: users                 Table: roles              Table: permissions
# ├─ id                        ├─ id                     ├─ id
# ├─ name                      ├─ name                   ├─ name
# ├─ email                     └─ description            └─ description
# └─ password
#
# Relationships (Many-to-Many):
# users (id=1) → user_roles → roles (id=2) → role_permissions → permissions
#
# Example:
# User "Alice" (id=1)
#   → has role "admin" (id=1)
#     → has permissions ["delete_user", "edit_post", "view_reports"]
# User "Bob" (id=2)
#   → has role "user" (id=2)
#     → has permissions ["view_posts", "create_comments"]
