"""
Seed script to create test users with known credentials.

WHY?
- Quick testing without going through API
- Known credentials for testing
- Easily recreate test data
- Foundation for automated testing
"""

from app import create_app
from app.models import User, Role, Permission
from app.extensions import db


def seed_test_users():
    """Create test users with known credentials."""
    app = create_app('development')

    with app.app_context():
        print("="*60)
        print("SEEDING TEST USERS")
        print("="*60)

        # Clear existing users (optional - comment out if you want to keep them)
        # User.query.delete()
        # db.session.commit()

        # Create test users
        test_users = [
            {
                "name": "Admin User",
                "email": "admin@test.com",
                "password": "admin123"
            },
            {
                "name": "John Doe",
                "email": "john@test.com",
                "password": "john123"
            },
            {
                "name": "Jane Smith",
                "email": "jane@test.com",
                "password": "jane123"
            },
            {
                "name": "Bob Johnson",
                "email": "bob@test.com",
                "password": "bob123"
            }
        ]

        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data["email"]).first()
            if existing:
                print(f"⚠️  User {user_data['email']} already exists, skipping...")
                continue

            # Create new user
            user = User(
                name=user_data["name"],
                email=user_data["email"]
            )
            user.set_password(user_data["password"])

            db.session.add(user)
            db.session.commit()

            print(f"✅ Created user: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print()

        print("="*60)
        print("TEST USERS CREATED!")
        print("="*60)
        print("\nYou can now use these credentials to login:")
        print()
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print()


if __name__ == '__main__':
    seed_test_users()
