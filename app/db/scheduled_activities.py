import sqlite3

def sync_scheduled_activities_with_database(scheduled_activities, user_id):
    database_scheduled_activities = get_scheduled_activities_from_database_as_tuples(user_id)

    for scheduled_activity in scheduled_activities:
        # Check if the scheduled activity already exists in the database
        exists = False

        for database_scheduled_activity in database_scheduled_activities:
            if scheduled_activity["title"] == database_scheduled_activity[1] and scheduled_activity["startTime"] == database_scheduled_activity[3] and scheduled_activity["endTime"] == database_scheduled_activity[4] and scheduled_activity["date"] == database_scheduled_activity[5] and user_id == database_scheduled_activity[6]:
                exists = True
                break

        if (not exists):

            # Add the scheduled activity to the database
            add_scheduled_activity_to_database(scheduled_activity, user_id)

    return True

def remove_scheduled_activity_from_database(scheduled_activity, user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Remove the scheduled activity from the database
    res = cur.execute("DELETE FROM ScheduledActivity WHERE Title = ? AND StartTime = ? AND EndTime = ? AND Date = ? AND UserID = ?;", (scheduled_activity["title"], scheduled_activity["startTime"], scheduled_activity["endTime"], scheduled_activity["date"], user_id))

    # Commit to database
    con.commit()
    con.close()

    return True

def get_scheduled_activities_from_database_as_dicts(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get all the scheduled activities associated with that user
    res = cur.execute("SELECT * FROM ScheduledActivity WHERE UserID = ?;", (user_id,))

    scheduled_activities = res.fetchall()
    if (len(scheduled_activities) == 0):
        return []
    else:
        # Scheduled activities need to be returned as a list of dicts in order to be sent as JSON
        scheduled_activity_dict_list = []
        for activity in scheduled_activities:
            # Get the category name
            category_name = cur.execute("SELECT Name FROM Category WHERE CategoryID = ?;", (activity[2],)).fetchone()[0]

            new_activity = {"title": activity[1], "category": category_name, "startTime": activity[3], "endTime": activity[4], "date": activity[5]}

            # Add to the list
            scheduled_activity_dict_list.append(new_activity)

        con.commit()
        con.close()

        return scheduled_activity_dict_list
    
def get_scheduled_activities_from_database_as_tuples(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get all the scheduled activities associated with that user
    res = cur.execute("SELECT * FROM ScheduledActivity WHERE UserID = ?;", (user_id,))

    scheduled_activities = res.fetchall()
    con.commit()
    con.close()

    if (len(scheduled_activities) == 0):
        return []
    else:
        return scheduled_activities

def add_scheduled_activities_to_database(scheduled_activities, user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Scheduled activities will be JSON (i.e. a dict of dicts)
    for activity in scheduled_activities:
        activity_title = activity["title"]
        activity_category = activity["category"]
        activity_start_time = activity["startTime"]
        activity_end_time = activity["endTime"]
        activity_date = activity["date"]

        # Get the correct CategoryID from the category table
        res = cur.execute("SELECT CategoryID FROM Category WHERE Name = ?;", (activity_category,))
        one_item_tuple = res.fetchone()
        if one_item_tuple == None:
            return False
        activity_category_id = one_item_tuple[0]

        # Insert the scheduled activity into the database
        res = cur.execute("INSERT INTO ScheduledActivity (Title, CategoryID, StartTime, EndTime, Date, UserID) VALUES (?, ?, ?, ?, ?, ?)", (activity_title, activity_category_id, activity_start_time, activity_end_time, activity_date, user_id))

    con.commit()
    con.close()
    return True

def add_scheduled_activity_to_database(scheduled_activity, user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get scheduled activity data
    activity_title = scheduled_activity["title"]
    activity_category = scheduled_activity["category"]
    activity_start_time = scheduled_activity["startTime"]
    activity_end_time = scheduled_activity["endTime"]
    activity_date = scheduled_activity["date"]

    # Get the correct CategoryID from the category table
    res = cur.execute("SELECT CategoryID FROM Category WHERE Name = ?;", (activity_category,))
    one_item_tuple = res.fetchone()
    if one_item_tuple == None:
        return False
    activity_category_id = one_item_tuple[0]

    # Add the scheduled activity to the database
    res = cur.execute("INSERT INTO ScheduledActivity (Title, CategoryID, StartTime, EndTime, Date, UserID) VALUES (?, ?, ?, ?, ?, ?)", (activity_title, activity_category_id, activity_start_time, activity_end_time, activity_date, user_id))

    con.commit()
    con.close()
    return True