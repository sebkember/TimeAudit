from flask import request, Blueprint

from ...utils.auth import authenticate_user, decode_jwt_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth", methods=["GET"])
def auth():
    authenticated = False
    expired = False
    if ("token" in request.cookies):
        token = request.cookies.get("token")
        authenticated = authenticate_user(token)
        # Check if the token has expired
        if (not authenticated):
            decoded_token = decode_jwt_token(token)
            if decoded_token["error"] == "expired_token":
                expired = True

    return {"authenticated": authenticated, "expired": expired}, 200