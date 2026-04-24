from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from flask import current_app

from app.extensions import db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.exceptions import AuthenticationError, TokenError


class AuthService:
    @staticmethod
    def register_user(name: str, email: str, password: str) -> tuple[dict, int]:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"message": "Email already registered"}, 409

        user = User(name=name, email=email)
        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Could not create user"}, 400

        return {"message": "User registered successfully", "user": user.to_dict()}, 201

    @staticmethod
    def login_user(email: str, password: str) -> tuple[dict, int]:
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {"message": "Invalid credentials"}, 401

        # =====================================================================
        # WHY get JWT expiration from config?
        # =====================================================================
        # Allows different expiration for dev vs production
        # Example: Dev: 15 min (easy testing), Prod: 5 min (security)
        # =====================================================================
        expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        access_token = create_access_token(identity=str(user.id), expires_delta=expires_delta)

        # =====================================================================
        # WHY create refresh token?
        # =====================================================================
        # Access token expires after 15 min
        # Refresh token lets user get new access token without re-typing password
        # Refresh token stored in DB so it can be revoked (logout)
        # =====================================================================
        refresh_token_str = create_access_token(
            identity=str(user.id),
            expires_delta=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        )

        # Store refresh token in database
        RefreshToken.create_token(
            user_id=user.id,
            token=refresh_token_str,
            expires_in_days=7
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token_str,
            "token_type": "Bearer",
            "user": user.to_dict(),
        }, 200

    @staticmethod
    def refresh_access_token(refresh_token_str: str) -> tuple[dict, int]:
        """
        Generate new access token from refresh token.

        WHY?
        - When access token expires (15 min), use refresh token to get new one
        - No need to login again (better UX)
        - Refresh token can be revoked (logout)

        Flow:
        1. Verify refresh token exists in DB
        2. Check it's not expired
        3. Generate new access token
        4. OPTIONAL: Rotate refresh token (security best practice)

        Security:
        - Refresh token stored in DB (can revoke)
        - Check expiration before validating
        - User can't use revoked tokens
        """
        # Verify refresh token exists and isn't expired
        refresh_token_obj = RefreshToken.verify_token(refresh_token_str)

        if not refresh_token_obj:
            raise TokenError("Invalid or expired refresh token")

        # Get user
        user = User.query.get(refresh_token_obj.user_id)
        if not user:
            raise TokenError("User not found")

        # =====================================================================
        # Create new access token
        # =====================================================================
        expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES')
        new_access_token = create_access_token(
            identity=str(user.id),
            expires_delta=expires_delta
        )

        # =====================================================================
        # Token Rotation (Security Best Practice)
        # =====================================================================
        # WHY rotate?
        # - Old refresh token becomes invalid after use
        # - If old token is stolen, it can't be used again
        # - Forces attacker to compromise both tokens
        #
        # How:
        # 1. Delete old refresh token
        # 2. Create new refresh token
        # 3. Return new tokens
        # =====================================================================

        # Create new refresh token
        new_refresh_token_str = create_access_token(
            identity=str(user.id),
            expires_delta=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES')
        )

        # Delete old refresh token (revoke it)
        db.session.delete(refresh_token_obj)

        # Store new refresh token
        RefreshToken.create_token(
            user_id=user.id,
            token=new_refresh_token_str,
            expires_in_days=7
        )

        return {
            "message": "Token refreshed successfully",
            "access_token": new_access_token,
            "refresh_token": new_refresh_token_str,
            "token_type": "Bearer",
            "user": user.to_dict(),
        }, 200

    @staticmethod
    def logout_user(user_id: int) -> tuple[dict, int]:
        """
        Logout user by revoking all their refresh tokens.

        WHY?
        - User clicks "logout"
        - Delete all refresh tokens from DB
        - User can't get new access tokens
        - Effectively logged out

        Implementation:
        - Find all refresh tokens for user
        - Delete them all
        - Next time they try to refresh → "Invalid token"
        """
        RefreshToken.revoke_all_for_user(user_id)

        return {
            "message": "Logout successful"
        }, 200

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> tuple[dict, int]:
        """
        Change user password.

        WHY?
        - User wants to change their password
        - Must verify old password first (security)
        - After change, logout user (force re-login for safety)

        Process:
        1. Get user from DB
        2. Verify old password matches
        3. Hash new password
        4. Update in DB
        5. Revoke all refresh tokens (logout user)
        """
        user = User.query.get(user_id)

        if not user:
            raise AuthenticationError("User not found")

        # Verify old password is correct
        if not user.check_password(old_password):
            raise AuthenticationError("Incorrect password")

        # Set new password (bcrypt hashing happens in set_password)
        user.set_password(new_password)
        db.session.commit()

        # Logout user by revoking all refresh tokens (security best practice)
        # Force user to re-login with new password
        RefreshToken.revoke_all_for_user(user_id)

        return {
            "message": "Password changed successfully. Please login again.",
            "user": user.to_dict()
        }, 200

    @staticmethod
    def update_profile(user_id: int, name: str = None, email: str = None) -> tuple[dict, int]:
        """
        Update user profile (name and/or email).

        WHY?
        - Users need to update their information
        - Email must be checked for duplicates
        - Partial updates allowed (just name or just email)

        Process:
        1. Get user from DB
        2. If email provided, check if already taken by someone else
        3. Update fields
        4. Commit to DB
        """
        user = User.query.get(user_id)

        if not user:
            raise AuthenticationError("User not found")

        # Update name if provided
        if name is not None:
            user.name = name

        # Update email if provided
        if email is not None:
            # Check if email already taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return {
                    "message": "Email already in use",
                    "error_code": "CONFLICT"
                }, 409

            user.email = email

        db.session.commit()

        return {
            "message": "Profile updated successfully",
            "user": user.to_dict()
        }, 200

