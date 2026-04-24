"""Seed script to create roles, permissions, and admin user."""

from app import create_app
from app.models import User, Role, Permission
from app.extensions import db


def seed_rbac():
    """Seed database with roles, permissions, and admin user."""
    app = create_app('development')

    with app.app_context():
        print("="*60)
        print("SEEDING RBAC DATA")
        print("="*60)

        # =====================================================================
        # WHY seed?
        # =====================================================================
        # - Create test data with known values
        # - Set up admin user for testing
        # - Create permissions for admin endpoints
        # - Repeatably set up database state
        # =====================================================================

        # Clear existing data (optional)
        # Role.query.delete()
        # Permission.query.delete()
        # User.query.delete()
        # db.session.commit()

        # =====================================================================
        # Step 1: Create Permissions
        # =====================================================================
        print("\n1. Creating permissions...")

        permissions_data = [
            ("view_users", "Can view all users"),
            ("delete_user", "Can delete users"),
            ("edit_user", "Can edit user profiles"),
            ("assign_roles", "Can assign roles to users"),
            ("view_reports", "Can view reports"),
        ]

        permissions = {}
        for perm_name, perm_desc in permissions_data:
            # Check if permission already exists
            existing = Permission.query.filter_by(name=perm_name).first()
            if existing:
                print(f"   ⚠️  Permission '{perm_name}' already exists")
                permissions[perm_name] = existing
            else:
                perm = Permission(name=perm_name, description=perm_desc)
                db.session.add(perm)
                permissions[perm_name] = perm
                print(f"Created permission: {perm_name}")

        db.session.commit()

        # =====================================================================
        # Step 2: Create Roles
        # =====================================================================
        print("\n2. Creating roles...")

        # Admin role - has ALL permissions
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            print("   ⚠️  Role 'admin' already exists")
        else:
            admin_role = Role(name='admin', description='Administrator with all permissions')
            admin_role.permissions = [permissions[key] for key in permissions.keys()]
            db.session.add(admin_role)
            print(f"   ✅ Created role: admin")
            print(f"      Permissions: {[p.name for p in admin_role.permissions]}")

        # User role - limited permissions
        user_role = Role.query.filter_by(name='user').first()
        if user_role:
            print("   ⚠️  Role 'user' already exists")
        else:
            user_role = Role(name='user', description='Regular user with limited permissions')
            user_role.permissions = [permissions['view_reports']]
            db.session.add(user_role)
            print(f"   ✅ Created role: user")
            print(f"      Permissions: {[p.name for p in user_role.permissions]}")

        # Moderator role - moderate permissions
        moderator_role = Role.query.filter_by(name='moderator').first()
        if moderator_role:
            print("   ⚠️  Role 'moderator' already exists")
        else:
            moderator_role = Role(
                name='moderator',
                description='Moderator - can manage content'
            )
            moderator_role.permissions = [
                permissions['view_users'],
                permissions['view_reports'],
            ]
            db.session.add(moderator_role)
            print(f"   ✅ Created role: moderator")
            print(f"      Permissions: {[p.name for p in moderator_role.permissions]}")

        db.session.commit()

        # =====================================================================
        # Step 3: Create Users
        # =====================================================================
        print("\n3. Creating users...")

        # Admin user
        admin_user = User.query.filter_by(email='admin@test.com').first()
        if admin_user:
            print("   ⚠️  Admin user already exists")
        else:
            admin_user = User(name='Admin User', email='admin@test.com')
            admin_user.set_password('AdminPass123')
            admin_user.assign_role(admin_role)
            db.session.add(admin_user)
            print(f"   ✅ Created user: admin@test.com")
            print(f"      Password: AdminPass123")
            print(f"      Role: admin")

        # Regular user
        regular_user = User.query.filter_by(email='user@test.com').first()
        if regular_user:
            print("   ⚠️  Regular user already exists")
        else:
            regular_user = User(name='Regular User', email='user@test.com')
            regular_user.set_password('UserPass123')
            regular_user.assign_role(user_role)
            db.session.add(regular_user)
            print(f"   ✅ Created user: user@test.com")
            print(f"      Password: UserPass123")
            print(f"      Role: user")

        # Moderator user
        mod_user = User.query.filter_by(email='mod@test.com').first()
        if mod_user:
            print("   ⚠️  Moderator user already exists")
        else:
            mod_user = User(name='Moderator User', email='mod@test.com')
            mod_user.set_password('ModPass123')
            mod_user.assign_role(moderator_role)
            db.session.add(mod_user)
            print(f"   ✅ Created user: mod@test.com")
            print(f"      Password: ModPass123")
            print(f"      Role: moderator")

        db.session.commit()

        # =====================================================================
        # Step 4: Verify Setup
        # =====================================================================
        print("\n4. Verification...")

        admin = User.query.filter_by(email='admin@test.com').first()
        if admin:
            print(f"   ✅ Admin user exists")
            print(f"      Roles: {[r.name for r in admin.roles]}")
            print(f"      Permissions: {admin.get_all_permissions()}")

        regular = User.query.filter_by(email='user@test.com').first()
        if regular:
            print(f"   ✅ Regular user exists")
            print(f"      Roles: {[r.name for r in regular.roles]}")
            print(f"      Permissions: {regular.get_all_permissions()}")

        print("\n" + "="*60)
        print("RBAC SEEDING COMPLETE!")
        print("="*60)
        print("\nTest credentials:")
        print("  Admin:     admin@test.com / AdminPass123")
        print("  Regular:   user@test.com / UserPass123")
        print("  Moderator: mod@test.com / ModPass123")


if __name__ == '__main__':
    seed_rbac()
