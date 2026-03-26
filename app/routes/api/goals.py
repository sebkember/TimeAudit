from flask import jsonify

from ...utils.auth import decode_jwt_token

from ...db.goals import get_goals_from_database_as_dicts, add_goals_to_database, remove_goal_from_database, update_goal_in_database, sync_goals_with_database

@app.route("/api/goals", methods=["GET", "POST"])
def goals_api():
    if (request.method == "GET"):
        # Get the token
        token = request.cookies["token"]
        decoded_token = decode_jwt_token(token)

        if ("error" in decoded_token):
            return {"error": "authentication_failed"}
        else:
            user_id = decoded_token["user-id"]

            # Get all goals from the database
            goals = get_goals_from_database_as_dicts(user_id)

            return jsonify(goals), 200

        pass
    elif (request.method == "POST"):
        # Frontend is posting goals to the server

        # List of goals posted to the server
        goals = request.get_json()

        # Get the token
        token = request.cookies.get("token")
        decoded_token = decode_jwt_token(token)

        # Check if the token is valid
        if ("error" in decoded_token):
            return {"error": "authentication_failed"}, 400
        else:
            # Get the user id
            user_id = decoded_token["user-id"]

            # Add the activities to the database
            result = add_goals_to_database(goals, user_id)

            # Check if writing to database was successful
            if (result):
                return {"success": True}, 200
            else:
                return {"error": "goals_added_failed"}, 500
            
@app.route("/api/goals/remove", methods=["POST"])
def remove_goal_api():
    # Get the goal
    goal = request.get_json()

    # Get the token
    token = request.cookies.get("token")
    decoded_token = decode_jwt_token(token)

    # Check if the token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id 
        user_id = decoded_token["user-id"]

        # Remove the goal from the database
        remove_goal_from_database(goal, user_id)

        return {"success": True}, 200
    
@app.route("/api/goals/update", methods=["POST"])
def update_goal_api():
    # Get the goal
    goal = request.get_json()

    # Get the token
    token = request.cookies.get("token")
    decoded_token = decode_jwt_token(token)

    # Check if the token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id 
        user_id = decoded_token["user-id"]

        # Update the goal in the database
        update_goal_in_database(goal, user_id)

        return {"success": True}, 200
    
@app.route("/api/goals/sync", methods=["POST"])
def sync_goals_api():
    # Get goals from request
    goals = request.get_json()

    # Get the token
    token = request.cookies["token"]
    decoded_token = decode_jwt_token(token)

    # Check if token is valid
    if ("error" in decoded_token):
        return {"error": "authentication_failed"}, 400
    else:
        # Get the user id
        user_id = decoded_token["user-id"]

        # Sync goals with the database
        result = sync_goals_with_database(goals, user_id)

        if (result):
            return {"success": True}, 200
        else:
            return {"error": "goals_sync_failed"}, 500