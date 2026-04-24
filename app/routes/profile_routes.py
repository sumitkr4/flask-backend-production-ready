from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User


profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/profile")
@jwt_required()
def profile():
    """
    Get logged-in user's profile (Protected endpoint).
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Profile fetched successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Profile fetched successfully"
            user:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                email:
                  type: string
      401:
        description: Missing or invalid JWT token
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Missing Authorization Header"
      404:
        description: User not found
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User not found"
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {"message": "User not found"}, 404

    return {"message": "Profile fetched successfully", "user": user.to_dict()}, 200

