from app.extensions import bcrypt, db


class User(db.Model):
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(120), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password: str = db.Column(db.String(255), nullable=False)

    # ============================================================================
    # RBAC: Relationship to roles
    # WHY?
    # - User can have multiple roles (e.g., both 'admin' and 'moderator')
    # - Access to roles easily: user.roles
    # - Query permissions through roles
    # ============================================================================
    roles = db.relationship(
        'Role',
        secondary='user_roles',  # Reference to user_roles association table
        backref=db.backref('users', lazy='dynamic')
    )

    def __init__(self, name: str, email: str, password: str = "") -> None:
        self.name = name
        self.email = email
        self.password = password

    def set_password(self, raw_password: str) -> None:
        hashed_password = bcrypt.generate_password_hash(raw_password).decode("utf-8")
        self.password = hashed_password

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password, raw_password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
        }

    # ============================================================================
    # RBAC Helper Methods
    # ============================================================================

    def has_role(self, role_name: str) -> bool:
        """
        Check if user has a specific role.

        WHY?
        - Quick way to check role: if user.has_role('admin')
        - More readable than: if any(r.name == 'admin' for r in user.roles)

        Example:
        >>> user = User.query.get(1)
        >>> if user.has_role('admin'):
        ...     # User can delete
        """
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if user has a specific permission through any role.

        WHY?
        - User doesn't have permissions directly, they flow through roles
        - Check: if user.has_permission('delete_user')
        - More efficient than checking each role manually

        Example:
        >>> user = User.query.get(1)
        >>> if user.has_permission('delete_user'):
        ...     # User can delete other users
        """
        for role in self.roles:
            for permission in role.permissions:
                if permission.name == permission_name:
                    return True
        return False

    def get_all_permissions(self) -> list:
        """
        Get all permissions for this user through all their roles.

        WHY?
        - Could be needed for frontend (show what user can do)
        - Useful for caching permissions
        - Debugging: see what user can do
        """
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.name)
        return list(permissions)

    def assign_role(self, role: 'Role') -> None:
        """Assign a role to user."""
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: 'Role') -> None:
        """Remove a role from user."""
        if role in self.roles:
            self.roles.remove(role)

