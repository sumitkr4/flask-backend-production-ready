"""
RefreshToken model for managing refresh tokens.

WHY store tokens in database?
- Logout (revoke token by deleting from DB)
- Check token exists before using it
- Prevent token reuse
- Track which devices/sessions are active
"""

from app.extensions import db
from datetime import datetime, timedelta


class RefreshToken(db.Model):
    """
    Model to store and manage refresh tokens.

    WHY?
    - JWTs are stateless, but we need some state (logout, revocation)
    - Store token in DB to verify it exists
    - Can revoke by deleting from DB
    - Can track user sessions

    Workflow:
    1. User logs in → create access + refresh token → store refresh_token in DB
    2. Access token expires → use refresh_token to get new access_token
    3. User logs out → delete refresh_token from DB (token revoked)
    """
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True)

    # WHY these fields?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    token = db.Column(db.String(500), unique=True, nullable=False, index=True)

    # Expiration tracking
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Track device/user agent (optional, for security)
    user_agent = db.Column(db.String(255))

    def __repr__(self):
        return f'<RefreshToken user_id={self.user_id} expires_at={self.expires_at}>'

    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def create_token(user_id: int, token: str, expires_in_days: int = 7, user_agent: str = None) -> 'RefreshToken':
        """
        Create a new refresh token.

        WHY static method?
        - Encapsulate token creation logic
        - Can be called without instance: RefreshToken.create_token(...)
        - Easy to test and reuse
        """
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            user_agent=user_agent
        )

        db.session.add(refresh_token)
        db.session.commit()

        return refresh_token

    @staticmethod
    def verify_token(token: str) -> 'RefreshToken':
        """
        Verify and get refresh token from DB.

        Returns None if:
        - Token doesn't exist
        - Token is expired
        """
        refresh_token = RefreshToken.query.filter_by(token=token).first()

        if refresh_token and not refresh_token.is_expired:
            return refresh_token

        return None

    @staticmethod
    def revoke_all_for_user(user_id: int) -> None:
        """
        Logout user by revoking all their refresh tokens.

        WHY?
        - User clicks "logout" → delete all refresh_tokens → can't refresh → logged out
        - More secure than just invalidating one token
        """
        RefreshToken.query.filter_by(user_id=user_id).delete()
        db.session.commit()


# ============================================================================
# WHY store Token in Database?
# ============================================================================
# Option 1: Pure JWT (stateless)
# ✅ Pro: No database lookup needed
# ❌ Con: Can't revoke (logout doesn't really logout)
#
# Option 2: JWT + Database (best of both)
# ✅ Pro: Stateless access tokens + logout capability
# ✅ Pro: Can track active sessions
# ✅ Pro: Can revoke specific tokens
# ❌ Con: Need database lookup on refresh
#
# We choose Option 2!
