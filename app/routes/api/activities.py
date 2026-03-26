from flask import jsonify, request, Blueprint
import json

from ...utils.auth import decode_jwt_token
from ...utils.streak import format_streak

from ...db.activities import get_activities_from_database_as_dicts, add_activities_to_database, remove_activity_from_database, sync_activities_with_database, update_activity_in_database, get_currently_running_activity, get_activity_id_from_database, add_activity_to_database, remove_running_activity_from_database
from ...db.users import update_streak, reset_streak_if_expired

activities_bp = Blueprint("activities", __name__)

@activities_bp.route("/api/activities", methods=["GET", "POST"])
def activities_api():
    if (request.method == "GET"):
        # Frontend is retrieving activities from the server

        # Token should already have been authenticated client-side so no need to do error checking
        token = request.cookies["token"]
        decoded_token = decode_jwt_token(token)
        if ("error" in decoded_token):
            return {"error": "invalid_token"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Get all activities from the server from that user
            activities = get_activities_from_database_as_dicts(user_id)

            # Return the activities
            return jsonify(activities), 200
    elif (request.method == "POST"):
        # Frontend is posting activities from the server

        # List of activities posted to the server
        activities = request.get_json()
        print(activities)

        # Get the token
        token = request.cookies.get("token")
        decoded_token = decode_jwt_token(token)

        if ("error" in decoded_token):
            return {"error": "authentication_failed"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Add the activities to the database
            result = add_activities_to_database(activities, user_id)

            # Update the user's streak
            updated_streak = update_streak(user_id)

            # Get a formatted string (with emoji) for the streak
            formatted_streak = format_streak(updated_streak)

            # Check if writing to database was successful
            if (result):
                return {"success": True, "streak": formatted_streak}, 200
            else:
                return {"error": "activities_added_failed"}, 500
            
@activities_bp.route("/api/activities/remove", methods=["POST"])
def remove_activity_api():
    # Get the activity
    activity = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if the token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id 
        user_id = decoded_token["user-id"]

        # Remove the activity from the database
        remove_activity_from_database(activity, user_id)

        # Reset the streak if activities_bplicable
        new_streak = reset_streak_if_expired(user_id)

        # Format the streak
        formatted_streak = format_streak(new_streak)

        return {"success": True, "streak": formatted_streak}, 200
    

    
@activities_bp.route("/api/activities/sync", methods=["POST"])
def sync_activities_api():
    # Get activities from request
    activities = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id
        user_id = decoded_token["user-id"]

        # Sync activities with the database
        result = sync_activities_with_database(activities, user_id)

        if (result):
            return {"success": True}, 200
        else:
            return {"error": "activities_sync_failed"}, 500
        
@activities_bp.route("/api/activities/edit", methods=["POST"])
def update_activity_api():
    # Get the request data
    request_data = request.get_json()

    # Get the activity
    activity = json.loads(request_data["activity"])

    # Get the activity id
    activity_id = request_data["id"]

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id
        user_id = decoded_token["user-id"]

        # Update the activity in the database
        result = update_activity_in_database(activity, activity_id, user_id)

        if (result):
            return {"success": True}, 200
        else:
            return {"error": "update_activity_failed"}, 500
        
@activities_bp.route("/api/activities/id", methods=["POST"])
def activity_id_api():
    # Get the activity
    activity = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id
        user_id = decoded_token["user-id"]

        # Get the activity id from the database
        activity_id = get_activity_id_from_database(activity, user_id)

        if (activity_id != -1):
            return {"success": True, "id": activity_id}, 200
        else:
            return {"error": "get_activity_id_failed"}, 500
        
@activities_bp.route("/api/activities/running", methods=["GET", "POST"])
def running_activity_api():
    if (request.method == "GET"):
        # Frontend is retrieving activity from the server

        # Token should already have been authenticated client-side so no need to do error checking
        token = request.cookies["token"]
        decoded_token = decode_jwt_token(token)
        if ("error" in decoded_token):
            return {"error": "invalid_token"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Get the currently running activity
            activity = get_currently_running_activity(user_id)

            print(activity)

            # Return the activity
            if (activity == None):
                return {"no_activity": True}, 200
            else:
                return activity, 200
    if (request.method == "POST"):
        # Frontend is posting activities from the server

        # List of activities posted to the server
        activity = request.get_json()
        print(activity)

        # Get the token
        token = request.cookies.get("token")
        decoded_token = decode_jwt_token(token)

        if ("error" in decoded_token):
            return {"error": "authentication_failed"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Add the activity to the database
            result = add_activity_to_database(activity, user_id, running=True)

            # Check if writing to database was successful
            if (result):
                return {"success": True}, 200
            else:
                return {"error": "activities_added_failed"}, 500
            
@activities_bp.route("/api/activities/running/stop", methods=["POST"])
def stop_running_activity_api():
    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    if ("error" in decoded_token):
        return {"error": "invalid_token"}, 400

    # Get the user id
    user_id = decoded_token["user-id"]

    # Remove the currently running activity from the database
    result = remove_running_activity_from_database(user_id)
    if (result):
        return {"success": True}, 200
    else:
        return {"error": "failed_to_stop_running_activity"}, 500