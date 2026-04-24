# Phase 1: 7-Day Learning & Implementation Plan

## Philosophy
**Learn by doing, understand before coding, validate after building**

---

## Daily Breakdown (7 Days)

### **Day 1: Foundation & Planning (4 hours)**

#### Morning (2 hours) - LEARNING
1. **Understand Pydantic** (30 min)
   - What: Data validation library
   - Why: Type checking, automatic validation
   - How: Read docs basic example
   - Q: Why better than manual validation?

2. **Understand RBAC Pattern** (45 min)
   - What: Role-Based Access Control
   - Why: Scalable permission system
   - How: Role → Permissions → Resources
   - Q: How does it differ from ACL?

3. **Understand Refresh Tokens** (45 min)
   - What: Two-token JWT strategy
   - Why: Security (short-lived access + long-lived refresh)
   - How: Access token (15min) vs Refresh token (7 days)
   - Q: Why not just one long-lived token?

#### Afternoon (2 hours) - PLANNING & SETUP
1. **Create Architecture Diagram** (30 min)
   - Draw: Models, Services, Routes, Auth flow
   - Document: How RBAC fits in
   - Reference: For implementation

2. **Plan Database Changes** (45 min)
   - New tables needed: roles, permissions, user_roles
   - Relationships to model
   - Migration strategy
   - Q: What if we need to backfill data?

3. **Setup Project Structure** (45 min)
   - Create new folders: schemas/, exceptions/, utils/
   - Update config for new features
   - Create `.md` documentation files

**Deliverable**: Architecture doc + updated project structure

---

### **Day 2: Validation Layer (5 hours)**

#### Morning (3 hours) - LEARNING + CODING
1. **Learn & Implement Pydantic Schemas** (2 hours)
   - Learn: Basic Pydantic models, validators
   - Code: Create `app/schemas/auth_schemas.py`
   - Implement:
     ```
     - UserRegisterSchema
     - UserLoginSchema
     - UserResponseSchema
     - TokenSchema
     ```
   - Task: Validate email format, password strength

2. **Understanding Request Validation** (1 hour)
   - Why validate on request?
   - Where to validate (route vs service)?
   - Best practice: Validate at boundary (routes)
   - Security: Prevent bad data earlier

#### Afternoon (2 hours) - IMPLEMENTATION
1. **Update Auth Routes to Use Pydantic** (1.5 hours)
   - Replace manual validation with Pydantic
   - Add error response formatting
   - Test with Postman
   - Q: How does Pydantic auto-generate errors?

2. **Create Profile Response Schema** (30 min)
   - Control what's returned (never expose password hash!)
   - Use `exclude_fields` concept
   - Test serialization

**Deliverable**: Working Pydantic validation in all auth endpoints

---

### **Day 3: User Roles & Permissions (5 hours)**

#### Morning (2.5 hours) - LEARNING
1. **Database Design for RBAC** (1 hour)
   - Models needed: Role, Permission, RolePermission
   - User-Role relationship (many-to-many)
   - Design decisions: Why this structure?
   - Draw: Entity Relationship Diagram

2. **RBAC Implementation Patterns** (1.5 hours)
   - Pattern 1: User → Role → Permission
   - Pattern 2: Decorators for route protection
   - Where to check: Model, Service, or Route?
   - Best practice: Check in service, expose in route

#### Afternoon (2.5 hours) - CODING
1. **Create Role & Permission Models** (1 hour)
   - Model: `app/models/role.py`, `permission.py`
   - Relationships with User model
   - Create migration

2. **Create Seed Script for Roles** (1 hour)
   - Seed: admin, user, moderator roles
   - Permissions: create_post, edit_post, delete_user, etc.
   - Script: `app/seeds/seed_roles.py`

3. **Test Models** (30 min)
   - Verify relationships
   - Test queries

**Deliverable**: RBAC database structure + seed data

---

### **Day 4: Custom Exceptions & Error Handling (4 hours)**

#### Morning (2 hours) - LEARNING
1. **Exception Design Patterns** (1 hour)
   - Custom exceptions hierarchy
   - When to raise vs return errors
   - Best practice: Fail fast, fail loud
   - Python exception best practices

2. **Structured Error Responses** (1 hour)
   - Consistent error format
   - Error codes vs HTTP status
   - Client understanding of errors

#### Afternoon (2 hours) - CODING
1. **Create Exception Classes** (1 hour)
   - `app/exceptions/__init__.py`
   - Classes: 
     ```
     - AuthenticationError
     - AuthorizationError
     - ValidationError
     - NotFoundError
     - ConflictError
     ```
   - Each has error code + message

2. **Update Routes to Use Exceptions** (1 hour)
   - Catch exceptions in routes
   - Convert to proper HTTP responses
   - Test error scenarios

**Deliverable**: Clean exception handling throughout app

---

### **Day 5: Refresh Tokens & JWT Improvements (5 hours)**

#### Morning (2.5 hours) - LEARNING
1. **JWT Deep Dive** (1.5 hours)
   - JWT structure: Header.Payload.Signature
   - Access token vs Refresh token strategy
   - Expiration and claims
   - Token revocation strategies

2. **Refresh Token Security** (1 hour)
   - Why rotate tokens?
   - How to revoke tokens?
   - Best practice: Store refresh tokens in DB

#### Afternoon (2.5 hours) - CODING
1. **Implement Refresh Token Flow** (1.5 hours)
   - Add `RefreshToken` model to store tokens
   - Create `/auth/refresh` endpoint
   - Rotate tokens on refresh
   - Revoke old tokens

2. **Update Login Response** (1 hour)
   - Return both access_token and refresh_token
   - Test complete flow
   - Verify token expiration

**Deliverable**: Working refresh token system

---

### **Day 6: Logging & Monitoring (4 hours)**

#### Morning (2 hours) - LEARNING
1. **Structured Logging** (1 hour)
   - Why JSON logs?
   - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Contextual logging (request_id, user_id)

2. **Logging Best Practices** (1 hour)
   - What to log: Decisions, errors, important flows
   - What NOT to log: Passwords, tokens
   - Log aggregation readiness

#### Afternoon (2 hours) - CODING
1. **Setup Logging Configuration** (1 hour)
   - Create `app/utils/logger.py`
   - JSON formatter
   - Ensure no sensitive data logged

2. **Add Logging Throughout App** (1 hour)
   - Log: registrations, logins, permission checks
   - Log: errors and exceptions
   - Test log output

**Deliverable**: Structured logging in all key endpoints

---

### **Day 7: Testing & Documentation (6 hours)**

#### Morning (3 hours) - LEARNING + CODING
1. **Unit Testing Basics** (1.5 hours)
   - Learn: pytest fixtures, mocking
   - Create: `tests/` folder structure
   - Test: Individual functions (services, models)

2. **Integration Testing** (1.5 hours)
   - Test: Full API flows with database
   - Use: Test database (SQLite in-memory)
   - Test scenarios: Register → Login → Access

#### Afternoon (3 hours) - IMPLEMENTATION
1. **Write Unit Tests** (1.5 hours)
   - Test auth_service methods
   - Test custom exceptions
   - Test RBAC logic
   - Target: 70% coverage

2. **Write Integration Tests** (1.5 hours)
   - Test: Full register flow
   - Test: Login with refresh token
   - Test: Protected route with RBAC
   - Test: Permission checks

**Deliverable**: Comprehensive test suite with 70%+ coverage

---

## Learning Approach for Each Day

### ✅ For EVERY FEATURE:
1. **Understand (30-45 min)**
   - Read documentation
   - Understand the "why"
   - Ask yourself questions
   - Look at examples

2. **Design (15-30 min)**
   - Sketch on paper/whiteboard
   - Document your approach
   - Think about edge cases
   - Get feedback (ask me!)

3. **Implement (60-90 min)**
   - Start coding
   - Run tests frequently
   - Don't rush
   - Ask questions when stuck

4. **Validate (15-30 min)**
   - Test your implementation
   - Check edge cases
   - Verify requirements
   - Document learnings

---

## How We'll Work Together

### What I'll Do:
- ✅ Explain concepts clearly (not just code)
- ✅ Ask YOU guiding questions first
- ✅ Point out best practices
- ✅ Review your code
- ✅ Suggest improvements
- ✅ Provide code only after discussion

### What You Should Do:
- ✅ Ask questions when confused
- ✅ Try implementing first before asking for code
- ✅ Read error messages carefully
- ✅ Document your learnings
- ✅ Review code you write
- ✅ Test frequently

---

## Daily Ritual (Do This Every Day)

### Morning (Start of Day)
```
1. Read the day's goals
2. Study the "Learning" section
3. Ask me questions about concepts
4. Discuss approach before coding
```

### During Coding
```
1. Code one feature at a time
2. Test after each small change
3. Ask for help when stuck (>10 min)
4. Review error messages
```

### Evening (End of Day)
```
1. Summarize what you learned
2. Document any insights
3. List tomorrow's goals
4. Note areas needing more practice
```

---

## Success Criteria

### By End of Day 5:
- ✅ Can explain RBAC to someone else
- ✅ Can implement custom exceptions
- ✅ Understand refresh tokens
- ✅ Comfortable with Pydantic

### By End of Day 7:
- ✅ All Phase 1 features working
- ✅ 70%+ test coverage
- ✅ Can explain architecture choices
- ✅ Ready for Phase 2

---

## Resources You Should Have

1. **Pydantic Docs**: https://docs.pydantic.dev/
2. **Flask-JWT-Extended**: https://flask-jwt-extended.readthedocs.io/
3. **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
4. **Pytest Guide**: https://docs.pytest.org/
5. **Python Best Practices**: PEP 8, PEP 20

---

## Red Flags (When to Ask for Help)

🚩 Stuck for >15 minutes on same problem
🚩 Getting errors you don't understand
🚩 Unsure about architectural decision
🚩 Test suite failing unexpectedly
🚩 Performance seems off
🚩 Code quality concerns

**Just ask!** No question is dumb. Learning is the goal.

---

## Tips for Success

1. **Commit regularly** - After each small feature works
2. **Take breaks** - Every 90 minutes, rest 15 min
3. **Review code daily** - Look at what you wrote yesterday
4. **Ask "why" repeatedly** - Understand, don't memorize
5. **Document as you go** - Future you will thank you
6. **Test edge cases** - Not just happy path
7. **Read error messages** - They're usually helpful
8. **Sleep well** - Learning needs rest

---

## Expected Challenges

| Challenge | Solution |
|-----------|----------|
| Pydantic feels complex | Start simple, build up |
| RBAC design confusing | Draw diagrams, discuss |
| JWT token issues | Test manually first |
| Tests failing | Debug one assertion at a time |
| Time pressure | Focus on core features first |
| Forgot concepts | Review previous days' notes |

---

## Phase 1 Completion Checklist

### Pydantic ✅
- [ ] All schemas created
- [ ] All routes use validation
- [ ] Error responses formatted

### RBAC ✅
- [ ] Role model created
- [ ] Permission model created
- [ ] Relationships working
- [ ] Decorator for @require_permission working

### Refresh Tokens ✅
- [ ] RefreshToken model created
- [ ] /auth/refresh endpoint working
- [ ] Token rotation implemented

### Custom Exceptions ✅
- [ ] Exception hierarchy created
- [ ] All errors use custom exceptions
- [ ] Error responses consistent

### Logging ✅
- [ ] Logger configured
- [ ] Key events logged
- [ ] No sensitive data logged

### Tests ✅
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] 70%+ coverage achieved
- [ ] All tests passing

---

## Next: Let's Start! 🚀

**Ready to begin Day 1?**

I'll guide you through:
1. Learning resources
2. Architecture planning
3. Project structure setup

We'll take it **step-by-step, discuss before coding**.

What do you think? Any questions about this approach?
