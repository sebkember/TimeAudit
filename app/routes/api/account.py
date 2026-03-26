from flask import make_response, request, Blueprint
from email_validator import validate_email, EmailNotValidError
import os

from ...utils.auth import decode_jwt_token
from ...utils.streak import format_streak
from ...db.users import delete_account, email_exists_in_database, update_email_address, reset_streak_if_expired

COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")

account_bp = Blueprint("account", __name__)

@account_bp.route("/api/logout", methods=["POST"])
def logout_api():
    # Get the token from the request
    token = request.cookies["token"]

    # Decode the token
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400

    # Reset the HttpOnly cookie
    response = make_response({"success": True}, 200)
    response.set_cookie("token", "", domain=COOKIE_DOMAIN, expires=0, httponly=True, secure=False, samesite='Lax')
    return response

@account_bp.route("/api/account/delete", methods=["POST"])
def delete_account_api():
    # Get the token from the request
    token = request.cookies["token"]

    # Decode the token
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400
    
    # Get the user id from the token
    user_id = decoded_token["user-id"]

    # Delete the user and all associated data from the database
    delete_account(user_id)

    # Reset the HttpOnly cookie
    response = make_response({"success": True}, 200)
    response.set_cookie("token", "", domain=COOKIE_DOMAIN, expires=0, httponly=True, secure=False, samesite='Lax')
    return response

@account_bp.route("/api/account/change-email", methods=["POST"])
def change_email_api():
    # Get the token from the request
    token = request.cookies["token"]

    # Decode the token
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400
    
    # Get the user id from the token
    user_id = decoded_token["user-id"]

    # Get the request body
    request_data = request.get_json()
    email_address = request_data["email-address"].strip()

    # If the email is invalid, return an error
    try:
        email_info = validate_email(email_address, check_deliverability=True)
        email_address = email_info.normalized
    except EmailNotValidError as e:
        print(str(e))
        return {"error": "invalid_email"}, 400

    # If the email already exists, return an error
    if (email_exists_in_database(email_address)):
        return {"error": "email_exists"}, 400

    # Update the email address
    update_email_address(user_id, email_address)

    return {"success": True}, 200

@account_bp.route("/api/account/update-streak", methods=["POST"])
def update_streak_api():
    # Get the token from the request
    token = request.cookies["token"]

    # Decode the token
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400
    
    # Get the user id from the token
    user_id = decoded_token["user-id"]

    # Update the user's streak
    updated_streak = reset_streak_if_expired(user_id)

    # Format the streak
    formatted_streak = format_streak(updated_streak)

    # Send the updated streak to the frontend
    return {"success": True, "streak": formatted_streak}, 200