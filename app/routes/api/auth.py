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
        print("lol")
        # Check if the token has expired
        if (not authenticated):
            decoded_token = decode_jwt_token(token)
            print("ERROR: " + decoded_token["error"])
            if decoded_token["error"] == "expired_token":
                expired = True

    return {"authenticated": authenticated, "expired": expired}, 200