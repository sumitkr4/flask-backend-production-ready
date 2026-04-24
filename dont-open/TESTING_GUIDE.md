# Flask Backend - Complete Testing Guide

## Project Overview
This is a production-ready Flask backend with:
- ✅ User authentication (Register/Login)
- ✅ JWT token-based authorization
- ✅ Password hashing with bcrypt
- ✅ SQLite database (SQLAlchemy ORM)
- ✅ Database migrations (Alembic/Flask-Migrate)
- ✅ Clean modular architecture with Services layer

## Architecture Analysis

### File Structure
```
app/
├── __init__.py          # Flask app factory pattern
├── config.py            # Environment-based config (Dev/Prod)
├── extensions.py        # Database, JWT, Bcrypt initialization
├── models/
│   └── user.py          # User model with password hashing
├── routes/
│   ├── auth_routes.py   # Register & Login endpoints
│   └── profile_routes.py # Protected profile endpoint
└── services/
    ├── auth_service.py  # Business logic for auth
    └── cache_service.py # Cache abstraction (extensible)
```

### Design Patterns Used
1. **Factory Pattern** - `create_app()` creates app instances
2. **Service Layer** - Business logic separated from routes
3. **Blueprint Architecture** - Modular route registration
4. **Extension Factory** - Centralized extension initialization

## Complete Testing Flow with Postman

### Setup
1. Flask app running: `python run.py` (running on http://127.0.0.1:5000)
2. Postman collection ready

### Test Sequence

#### **Test 1: User Registration**
```
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}

Expected: 201 Created
Response:
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

#### **Test 2: User Login**
```
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Expected: 200 OK
Response:
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```
**Save the `access_token` for next test!**

#### **Test 3: Get Protected Profile**
```
GET /profile
Authorization: Bearer <your_access_token>
Content-Type: application/json

Expected: 200 OK
Response:
{
  "message": "Profile fetched successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

---

## Error Scenarios (Validation Testing)

### Test 4: Duplicate Email Registration
```
POST /auth/register
{
  "name": "Jane Doe",
  "email": "john@example.com",  // Already exists
  "password": "newpass"
}

Expected: 409 Conflict
Response: {"message": "Email already registered"}
```

### Test 5: Wrong Password Login
```
POST /auth/login
{
  "email": "john@example.com",
  "password": "wrongpassword"
}

Expected: 401 Unauthorized
Response: {"message": "Invalid credentials"}
```

### Test 6: Missing Required Fields
```
POST /auth/register
{
  "name": "John",
  // Missing email and password
}

Expected: 400 Bad Request
Response: {"message": "name, email and password are required"}
```

### Test 7: Invalid JWT Token
```
GET /profile
Authorization: Bearer invalid_token_here

Expected: 401 Unauthorized
Response: {"msg": "Signature verification failed"}
```

### Test 8: Missing Authorization Header
```
GET /profile
// No Authorization header

Expected: 401 Unauthorized
Response: {"msg": "Missing Authorization Header"}
```

---

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL  -- bcrypt hashed
);
```

---

## Security Features ✅
- ✅ Passwords hashed with bcrypt (salted)
- ✅ JWT tokens for stateless authentication
- ✅ Email uniqueness constraint
- ✅ Input validation on all endpoints
- ✅ Error handlers for 400, 401, 404, 500
- ✅ Secure config management with .env

---

## Environment Configuration

### Development (.env)
```
FLASK_ENV=development
DATABASE_URL=sqlite:///flask_dev_db.sqlite
JWT_SECRET_KEY=super-secret-jwt-key-for-development-only
```

### Production (to configure)
```
FLASK_ENV=production
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
JWT_SECRET_KEY=<generate-strong-secret>
```

---

## Running the Application

### Initial Setup
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask db init
flask db migrate -m "initial"
flask db upgrade
```

### Run Server
```bash
python run.py
```

### Run Tests (when test suite added)
```bash
pytest
```

---

## Extensibility Points

### 1. Add Redis Caching
- Update `cache_service.py` with RedisCache implementation
- No route changes needed (abstraction layer ready)

### 2. Add More Models
- Create in `app/models/`
- Register with SQLAlchemy in extensions
- Create migrations automatically

### 3. Add New Routes
- Create blueprint in `app/routes/`
- Add service logic in `app/services/`
- Register blueprint in `app/routes/__init__.py`

### 4. Add Email Notifications
- Create `app/services/email_service.py`
- Call from `auth_service.py` after registration/reset

---

## Summary
✅ **All endpoints tested and working**
✅ **Complete user flow: Register → Login → AccessProtected**
✅ **Error handling validated**
✅ **Production-ready code structure**
✅ **Easy to extend and maintain**
