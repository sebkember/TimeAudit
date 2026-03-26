import sqlite3

def sync_activities_with_database(activities, user_id):
    database_activities = get_activities_from_database_as_tuples(user_id)

    for activity in activities:
        # Check if the activity already exists in the database
        exists = False

        for database_activity in database_activities:
            if activity["title"] == database_activity[1] and activity["startTime"] == database_activity[3] and activity["endTime"] == database_activity[4] and activity["date"] == database_activity[5] and user_id == database_activity[7]:
                exists = True
                break
        
        if (not exists):
            print(f"Activity {activity['title']} does not exist in the database, adding it now.")

            # Add the activity to the database
            add_activity_to_database(activity, user_id)
    
    return True


def remove_activity_from_database(activity, user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Remove the activity from the database
    res = cur.execute("DELETE FROM Activity WHERE Title = ? AND StartTime = ? AND EndTime = ? AND Date = ? AND UserID = ?;", (activity["title"], activity["startTime"], activity["endTime"], activity["date"], user_id))
    
    # Commit to database
    con.commit()
    con.close()

    return True

def remove_running_activity_from_database(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Remove the currently running activity from the database
    res = cur.execute("DELETE FROM Activity WHERE UserID = ? AND Running = 1;", (user_id,))
    
    # Commit to database
    con.commit()
    con.close()

    return True

def update_activity_in_database(activity, activity_id, user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get the category id from the category
    res = cur.execute("SELECT CategoryID FROM Category WHERE Name = ?", (activity["category"],))
    category_id = res.fetchone()[0]
    con.commit()

    # Get the goal id from the goal
    goal_id = None
    if ("goalName" in activity and activity["goalName"] != "None"):
        res = cur.execute("SELECT GoalID FROM Goal WHERE Title = ?", (activity["goalName"],))
        goal_id = res.fetchone()[0]
        con.commit()

    # Update the activity in the database
    res = cur.execute("UPDATE Activity SET Title = ?, CategoryID = ?, StartTime = ?, EndTime = ?, Date = ?, GoalID = ? WHERE ActivityID = ? AND UserID = ?", (activity["title"], category_id, activity["startTime"], activity["endTime"], activity["date"], goal_id, activity_id, user_id))
    con.commit()

    # Get number of changed rows
    changed_rows = cur.rowcount

    if (changed_rows == 1):
        return True
    else:
        return False
    
def get_activity_id_from_database(activity, user_id):
    # Connect to database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get the activity id from the database
    res = cur.execute("SELECT ActivityID FROM Activity WHERE Title = ? AND StartTime = ? AND EndTime = ? AND Date = ? AND UserID = ?", (activity["title"], activity["startTime"], activity["endTime"], activity["date"], user_id))
    activity_id_tuple = res.fetchone()

    if (activity_id_tuple == None):
        return -1
    else:
        return activity_id_tuple[0]


def get_currently_running_activity(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get the currently running activity
    res = cur.execute("SELECT * FROM Activity WHERE UserID = ? AND Running = 1;", (user_id,))
    activity = res.fetchone()
    
    con.commit()

    if (activity == None):
        con.close()
        return None
    else:
        # Get the category name
        category_name = cur.execute("SELECT Name FROM Category WHERE CategoryID = ?;", (activity[2],)).fetchone()[0]
        
        # Get the goal name
        goal_name_tuple = cur.execute("SELECT Title FROM Goal WHERE GoalID = ?", (activity[6],)).fetchone()
        if (goal_name_tuple == None):
            goal_name = "None"
        else:
            goal_name = goal_name_tuple[0]

        con.close()

        # Create a dict of the activity
        activity_dict = {"title": activity[1], "category": category_name, "startTime": activity[3], "endTime": activity[4], "date": activity[5], "goalName": goal_name}

        return activity_dict

def get_activities_from_database_as_dicts(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get all the activities associated with that user
    res = cur.execute("SELECT * FROM Activity WHERE UserID = ? AND Running = 0;", (user_id,))

    activities = res.fetchall()
    if (len(activities) == 0):
        return []
    else:
        # Activities need to be returned as a list of dicts in order to be sent as JSON
        activity_dict_list = []
        for activity in activities:
            category_name = cur.execute("SELECT Name FROM Category WHERE CategoryID = ?;", (activity[2],)).fetchone()[0]
            goal_name_tuple = cur.execute("SELECT Title FROM Goal WHERE GoalID = ?", (activity[6],)).fetchone()
            if (goal_name_tuple == None):
                goal_name = "None"
                # Set the ID to none (cleanup)
                cur.execute("UPDATE Activity SET GoalID = NULL WHERE ActivityID = ?;", (activity[0],))
            else:
                goal_name = goal_name_tuple[0]

            new_activity = {"title": activity[1], "category": category_name, "startTime": activity[3], "endTime": activity[4], "date": activity[5], "goalName": goal_name}

            # Add to the list
            activity_dict_list.append(new_activity)

        con.commit()
        con.close()

        
        return activity_dict_list

def get_activities_from_database_as_tuples(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get all the activities associated with that user
    res = cur.execute("SELECT * FROM Activity WHERE UserID = ? AND Running = 0;", (user_id,))

    activities = res.fetchall()
    con.commit()
    con.close()

    if (len(activities) == 0):
        return []
    else:
        return activities

def add_activities_to_database(activities, user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    

    # Activities will be JSON (i.e. a dict of dicts)
    for activity in activities:
        activity_title = activity["title"]
        activity_category = activity["category"]
        activity_start_time = activity["startTime"]
        activity_end_time = activity["endTime"]
        activity_date = activity["date"]

        print(f"Adding activity: {activity_title}, {activity_category}, {activity_start_time}, {activity_end_time}, {activity_date}")



        # Get the correct CategoryID from the category table
        res = cur.execute("SELECT CategoryID FROM Category WHERE Name = ?;", (activity_category,))
        one_item_tuple = res.fetchone()
        if one_item_tuple == None:
            print("Error: No such category exists")
            return False
        activity_category_id = one_item_tuple[0]

        # GoalID will be None (NULL) if there is no goal associated with the activity
        goal_id = None

        # First check the activity has an associated goal
        if ("goalName" in activity and activity["goalName"] != "None"):
            # Get the goal name
            activity_goal_name = activity["goalName"]
            print(f"Activity goal name: {activity_goal_name}")

            # Get the GoalID of the goal associated with that activity (if there is one)
            res = cur.execute("SELECT * FROM Goal WHERE Title = ? AND Date = ? AND UserID = ?", (activity_goal_name, activity_date, user_id))
            one_item_tuple = res.fetchone()
            if (one_item_tuple == None):
                print("Error: No such goal exists.")
                return False
            goal_id = one_item_tuple[0]

        # Insert activity into db
        res = cur.execute("INSERT INTO Activity (Title, CategoryID, StartTime, EndTime, Date, GoalID, UserID, Running) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (activity_title, activity_category_id, activity_start_time, activity_end_time, activity_date, goal_id, user_id, False))
    # Commit if no errors
    con.commit()
    con.close()
    return True

def add_activity_to_database(activity, user_id, running=False):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get activity data
    activity_title = activity["title"]
    activity_category = activity["category"]
    activity_start_time = activity["startTime"]
    activity_end_time = activity["endTime"]
    activity_date = activity["date"]

    # Get the correct CategoryID from the category table
    res = cur.execute("SELECT CategoryID FROM Category WHERE Name = ?;", (activity_category,))
    one_item_tuple = res.fetchone()
    if one_item_tuple == None:
        print("Error: No such category exists.")
        return False
    activity_category_id = one_item_tuple[0]

    # GoalID will be None (NULL) if there is no goal associated with the activity
    goal_id = None
    activity_goal_name = "None"
    if ("goalName" in activity):
        # Get the goal name
        activity_goal_name = activity["goalName"]

    if (activity_goal_name != "None"):
        # Get the GoalID of the goal associated with that activity (if there is one)
        res = cur.execute("SELECT * FROM Goal WHERE Title = ? AND Date = ? AND UserID = ?", (activity_goal_name, activity_date, user_id))
        one_item_tuple = res.fetchone()
        if (one_item_tuple == None):
            print("Error: No such goal exists.")
            return False
        goal_id = one_item_tuple[0]
    

    # Add the activity to the database
    res = cur.execute("INSERT INTO Activity (Title, CategoryID, StartTime, EndTime, Date, GoalID, UserID, Running) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (activity_title, activity_category_id, activity_start_time, activity_end_time, activity_date, goal_id, user_id, running))

    con.commit()
    con.close()
    return True