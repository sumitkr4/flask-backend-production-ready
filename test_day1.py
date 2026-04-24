"""
Test script to verify new models work correctly.

WHY a test script?
- Quick way to verify models without hitting API
- Test database queries directly
- Test model methods (has_role, has_permission, etc.)
- Foundation for unit tests
"""

from app import create_app
from app.models import User, Role, Permission, RefreshToken
from app.extensions import db
from datetime import datetime, timedelta


def test_create_roles_and_permissions():
    """Test creating roles and permissions."""
    app = create_app('development')

    with app.app_context():
        print("="*60)
        print("TEST 1: Create Roles and Permissions")
        print("="*60)

        # Clear existing data (for testing only)
        Role.query.delete()
        Permission.query.delete()
        db.session.commit()

        # Create permissions
        perm_delete_user = Permission(
            name='delete_user',
            description='Can delete other users'
        )
        perm_edit_user = Permission(
            name='edit_user',
            description='Can edit user profiles'
        )
        perm_view_reports = Permission(
            name='view_reports',
            description='Can view reports'
        )

        # Create roles
        role_admin = Role(
            name='admin',
            description='Administrator with all permissions'
        )
        role_user = Role(
            name='user',
            description='Regular user with limited permissions'
        )

        # Assign permissions to roles
        role_admin.permissions.extend([perm_delete_user, perm_edit_user, perm_view_reports])
        role_user.permissions.append(perm_view_reports)

        # Save to database
        db.session.add_all([perm_delete_user, perm_edit_user, perm_view_reports])
        db.session.add_all([role_admin, role_user])
        db.session.commit()

        print(f"✅ Created permissions: {[p.name for p in [perm_delete_user, perm_edit_user, perm_view_reports]]}")
        print(f"✅ Created roles: {[r.name for r in [role_admin, role_user]]}")
        print(f"  - admin role permissions: {[p.name for p in role_admin.permissions]}")
        print(f"  - user role permissions: {[p.name for p in role_user.permissions]}")
        print()


def test_user_rbac():
    """Test user RBAC methods."""
    app = create_app('development')

    with app.app_context():
        print("="*60)
        print("TEST 2: User RBAC Methods")
        print("="*60)

        # Get roles
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()

        # Get a user (or create one)
        alice = User.query.filter_by(email='alice@test.com').first()

        if not alice:
            print("⚠️  Alice user not found. Create user first via API.")
            return

        # Assign admin role to user
        alice.assign_role(admin_role)
        db.session.commit()

        print(f"✅ Assigned admin role to {alice.name}")
        print(f"  - has_role('admin'): {alice.has_role('admin')}")
        print(f"  - has_role('user'): {alice.has_role('user')}")
        print(f"  - has_permission('delete_user'): {alice.has_permission('delete_user')}")
        print(f"  - has_permission('edit_user'): {alice.has_permission('edit_user')}")
        print(f"  - has_permission('view_reports'): {alice.has_permission('view_reports')}")
        print(f"  - All permissions: {alice.get_all_permissions()}")
        print()


def test_refresh_token():
    """Test RefreshToken model."""
    app = create_app('development')

    with app.app_context():
        print("="*60)
        print("TEST 3: RefreshToken Model")
        print("="*60)

        # Get a user
        alice = User.query.filter_by(email='alice@test.com').first()

        if not alice:
            print("⚠️  Alice user not found. Create user first via API.")
            return

        # Create a refresh token
        test_token = "test_refresh_token_12345"
        refresh_token = RefreshToken.create_token(
            user_id=alice.id,
            token=test_token,
            expires_in_days=7,
            user_agent="TestBrowser/1.0"
        )

        print(f"✅ Created refresh token for {alice.name}")
        print(f"  - Token: {refresh_token.token[:20]}...")
        print(f"  - Expires at: {refresh_token.expires_at}")
        print(f"  - Is expired: {refresh_token.is_expired}")
        print()

        # Verify token
        verified_token = RefreshToken.verify_token(test_token)
        print(f"✅ Verified token:")
        print(f"  - Found: {verified_token is not None}")
        print(f"  - User ID: {verified_token.user_id if verified_token else None}")
        print()

        # Test expired token
        expired_token = RefreshToken(
            user_id=alice.id,
            token="expired_token_test",
            expires_at=datetime.utcnow() - timedelta(days=1),
            user_agent="TestBrowser/1.0"
        )
        db.session.add(expired_token)
        db.session.commit()

        verified_expired = RefreshToken.verify_token("expired_token_test")
        print(f"✅ Expired token check:")
        print(f"  - Expired token found and valid: {verified_expired is not None}")
        print(f"  - (Should be False/None because it's expired)")
        print()


def test_pydantic_schemas():
    """Test Pydantic schemas."""
    from app.schemas import RegisterSchema, LoginSchema, UserResponseSchema

    print("="*60)
    print("TEST 4: Pydantic Schemas Validation")
    print("="*60)

    # Test RegisterSchema
    try:
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "securepass123"
        }
        schema = RegisterSchema(**data)
        print(f"✅ RegisterSchema valid:")
        print(f"  - name: {schema.name}")
        print(f"  - email: {schema.email}")
        print()
    except Exception as e:
        print(f"❌ RegisterSchema error: {e}")
        print()

    # Test invalid email
    try:
        data = {
            "name": "John",
            "email": "invalid-email",
            "password": "pass"
        }
        schema = RegisterSchema(**data)
        print("❌ Should have failed (invalid email)")
    except Exception as e:
        print(f"✅ RegisterSchema correctly rejected invalid email:")
        print(f"  - Error: {str(e)[:100]}")
        print()

    # Test short password
    try:
        data = {
            "name": "John",
            "email": "john@example.com",
            "password": "short"
        }
        schema = RegisterSchema(**data)
        print("❌ Should have failed (short password)")
    except Exception as e:
        print(f"✅ RegisterSchema correctly rejected short password:")
        print(f"  - Error: {str(e)[:100]}")
        print()


def test_custom_exceptions():
    """Test custom exceptions."""
    from app.exceptions import (
        AuthenticationError,
        AuthorizationError,
        ValidationError,
        ConflictError,
        NotFoundError,
    )

    print("="*60)
    print("TEST 5: Custom Exceptions")
    print("="*60)

    tests = [
        ("AuthenticationError", AuthenticationError("Wrong password")),
        ("AuthorizationError", AuthorizationError("You lack admin role")),
        ("ValidationError", ValidationError("Email is required")),
        ("ConflictError", ConflictError("Email already registered")),
        ("NotFoundError", NotFoundError("User not found")),
    ]

    for name, exception in tests:
        print(f"✅ {name}:")
        print(f"  - message: {exception.message}")
        print(f"  - status_code: {exception.status_code}")
        print(f"  - error_code: {exception.error_code}")
    print()


if __name__ == '__main__':
    print("\n" + "="*60)
    print("CHECKPOINT TESTS - DAY 1 VERIFICATION")
    print("="*60 + "\n")

    # Run all tests
    test_create_roles_and_permissions()
    test_user_rbac()
    test_refresh_token()
    test_pydantic_schemas()
    test_custom_exceptions()

    print("="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run this script to verify everything works")
    print("2. Day 2: Connect schemas to routes")
    print("3. Day 2: Implement validation in endpoints")
