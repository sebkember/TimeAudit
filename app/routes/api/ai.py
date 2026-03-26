from app import limiter
from flask import Blueprint, request

from ...utils.auth import decode_jwt_token
from ...utils.ai import generate_user_schedule

generate_bp = Blueprint("generate-schedule", __name__)

@generate_bp.route("/api/account/generate-schedule", methods=["POST"])
@limiter.limit("5 per hour")
def generate_schedule_api():
    # Get the token from the request
    token = request.cookies["token"]

    # Decode the token
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400

    # Get the user id from the token
    user_id = decoded_token["user-id"]

    # Get the date from the request
    request_data = request.get_json()
    date = request_data["date"]
    startTime = request_data["startTime"]
    endTime = request_data["endTime"]

    # Generate the user's schedule
    schedule = generate_user_schedule(user_id, date, startTime, endTime) 
    #schedule = '[{"title": "Maths revision", "category": "Work/Study", "startTime": 510, "endTime": 600, "date": "2025-08-01"}]'  # Placeholder for testing

    return {"success": True, "schedule": schedule}, 200