from flask import jsonify, request, Blueprint

from ...utils.auth import decode_jwt_token

from ...db.scheduled_activities import get_scheduled_activities_from_database_as_dicts, add_scheduled_activities_to_database, remove_scheduled_activity_from_database, sync_scheduled_activities_with_database

scheduled_activities_bp = Blueprint("scheduled-activities", __name__)

@scheduled_activities_bp.route("/api/scheduled-activities", methods=["GET", "POST"])
def scheduled_activities_api():
    if (request.method == "GET"):
        # Frontend is retrieving scheduled activities from the server

        # Token should already have been authenticated client-side so no need to do error checking
        token = request.cookies["token"]
        decoded_token = decode_jwt_token(token)
        if ("error" in decoded_token):
            return {"error": "invalid_token"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Get all scheduled activities from the server from that user
            scheduled_activities = get_scheduled_activities_from_database_as_dicts(user_id)

            # Return the scheduled activities
            return jsonify(scheduled_activities), 200
    elif (request.method == "POST"):
        # Frontend is posting scheduled activities from the server

        # List of scheduled activities posted to the server
        scheduled_activities = request.get_json()
        print(scheduled_activities)

        # Get the token
        token = request.cookies.get("token")
        decoded_token = decode_jwt_token(token)

        if ("error" in decoded_token):
            return {"error": "authentication_failed"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Add the scheduled activities to the database
            result = add_scheduled_activities_to_database(scheduled_activities, user_id)

            # Check if writing to database was successful
            if (result):
                return {"success": True}, 200
            else:
                return {"error": "scheduled_activities_added_failed"}, 500
            
@scheduled_activities_bp.route("/api/scheduled-activities/remove", methods=["POST"])
def remove_scheduled_activity_api():
    # Get the scheduled activity
    scheduled_activity = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if the token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id 
        user_id = decoded_token["user-id"]

        # Remove the scheduled activity from the database
        remove_scheduled_activity_from_database(scheduled_activity, user_id)

        return {"success": True}, 200
    
@scheduled_activities_bp.route("/api/scheduled-activities/sync", methods=["POST"])
def sync_scheduled_activities_api():
    # Get scheduled activities from request
    scheduled_activities = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id
        user_id = decoded_token["user-id"]

        # Sync scheduled activities with the database
        result = sync_scheduled_activities_with_database(scheduled_activities, user_id)

        if (result):
            return {"success": True}, 200
        else:
            return {"error": "scheduled_activities_sync_failed"}, 500