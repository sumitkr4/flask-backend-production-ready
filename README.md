# Production-Ready Flask Backend (Learning Friendly)

This project uses Flask with a clean modular structure, JWT authentication, bcrypt password hashing, PostgreSQL + SQLAlchemy, and migration-ready setup.

## Project Structure

- app/
  - __init__.py
  - config.py
  - extensions.py
  - models/
    - __init__.py
    - user.py
  - routes/
    - __init__.py
    - auth_routes.py
    - profile_routes.py
  - services/
    - __init__.py
    - auth_service.py
    - cache_service.py
- migrations/
  - README.md
- .env.example
- .gitignore
- requirements.txt
- run.py

## File-by-File Explanation

1. app/__init__.py
- Contains create_app(), which is the Factory Pattern entry point.
- Loads environment variables.
- Applies config, initializes extensions, registers blueprints, and error handlers.

2. app/config.py
- Central configuration classes for development and production.
- Reads sensitive values from environment variables.

3. app/extensions.py
- Uses a simple Creational Pattern via ExtensionFactory class.
- Creates db, migrate, bcrypt, jwt in one place.
- initialize_extensions(app) binds these instances to the Flask app.

4. app/models/user.py
- SQLAlchemy User model with id, name, email, password.
- Password methods use bcrypt hashing and verification.

5. app/services/auth_service.py
- Business logic for register and login.
- Keeps route functions clean and focused.
- Generates JWT token after successful login.

6. app/services/cache_service.py
- Cache abstraction layer for future Redis integration.
- NullCacheService is a placeholder now and can be replaced by Redis implementation later.

7. app/routes/auth_routes.py
- /auth/register endpoint.
- /auth/login endpoint.
- Input validation and service-layer usage.

8. app/routes/profile_routes.py
- /profile protected endpoint.
- Requires JWT token using @jwt_required().

9. app/routes/__init__.py
- Registers blueprints in a centralized way.

10. run.py
- App entry point for local execution.

11. migrations/README.md
- Notes for migration workflow.

12. .env.example
- Example environment variables.

13. requirements.txt
- Project dependency list.

## Setup

1. Create and activate virtual environment
- Windows PowerShell:
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1

2. Install dependencies
- pip install -r requirements.txt

3. Create your .env
- Copy .env.example to .env and update values.

4. Run database migrations
- Set Flask app:
  - $env:FLASK_APP = "run.py"
- Initialize migrations first time only:
  - flask db init
- Generate migration:
  - flask db migrate -m "initial"
- Apply migration:
  - flask db upgrade

5. Run app
- python run.py

## API Endpoints

1. Register
- POST /auth/register
- Body:
  {
    "name": "Alice",
    "email": "alice@example.com",
    "password": "secret123"
  }

2. Login
- POST /auth/login
- Body:
  {
    "email": "alice@example.com",
    "password": "secret123"
  }
- Returns access_token

3. Profile (Protected)
- GET /profile
- Header:
  Authorization: Bearer <access_token>

## Why this design

- Factory Pattern keeps app creation testable and clean.
- Creational Pattern in extensions centralizes object creation.
- Services layer separates business logic from routes.
- Blueprints make modules scalable.
- Cache abstraction enables easy Redis addition later.
