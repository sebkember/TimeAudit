import sqlite3
from ..utils.dates import get_current_iso_date

def add_goals_to_database(goals, user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()
    # Goals will be JSON (i.e. a dict of dicts)
    for goal in goals:
        # Add the goal information to the database
        goal_title = goal["title"]
        goal_duration = goal["duration"]
        goal_time_done = goal["timeDone"]
        goal_date = goal["date"]

        # Insert the goal into the database
        res = cur.execute("INSERT INTO Goal (Title, Duration, TimeDone, Date, UserID) VALUES (?, ?, ?, ?, ?);", (goal_title, goal_duration, goal_time_done, goal_date, user_id))
    con.commit()
    con.close()
    return True

def add_goal_to_database(goal, user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get goal data
    goal_title = goal["title"]
    goal_duration = goal["duration"]
    goal_time_done = goal["timeDone"]
    goal_date = goal["date"]

    # Insert the goal into the database
    res = cur.execute("INSERT INTO Goal (Title, Duration, TimeDone, Date, UserID) VALUES (?, ?, ?, ?, ?);", (goal_title, goal_duration, goal_time_done, goal_date, user_id))
    
    # Commit to database
    con.commit()
    con.close()

    return True

def update_goal_in_database(goal, user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Update the goal in the database
    res = cur.execute("UPDATE Goal SET TimeDone = ? WHERE Title = ? AND Duration = ? AND Date = ? AND UserID = ?;", (goal["timeDone"], goal["title"], goal["duration"], goal["date"], user_id))

    # Commit to database
    con.commit()
    con.close()

    return True

def remove_goal_from_database(goal, user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Remove the goal from the database
    res = cur.execute("DELETE FROM Goal WHERE Title = ? AND Duration = ? AND TimeDone = ? AND Date = ? AND UserID = ?", (goal["title"], goal["duration"], goal["timeDone"], goal["date"], user_id))
    
    # Commit to database
    con.commit()
    con.close()

    return True

def sync_goals_with_database(goals, user_id):
    database_goals = get_goals_from_database_as_tuples(user_id)

    for goal in goals:
        # Check if the goal already exists in the database
        exists = False

        for database_goal in database_goals:
            if goal["title"] == database_goal[1] and goal["duration"] == database_goal[2] and goal["timeDone"] == database_goal[3] and goal["date"] == database_goal[4] and user_id == database_goal[5]:
                exists = True
                break
        
        if (not exists):

            # Add the goal to the database
            add_goal_to_database(goal, user_id)

    return True

def get_goals_from_database_as_tuples(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get all the goals associated with that user
    res = cur.execute("SELECT * FROM Goal WHERE UserID = ?;", (user_id,))
    goals = res.fetchall()
    con.commit()
    con.close()
    if (len(goals) == 0):
        return []
    else:
        return goals
    
def get_goals_from_database_as_dicts(user_id):
    dict_list = []

    goal_tuples = get_goals_from_database_as_tuples(user_id)

    for goal in goal_tuples:
        goal_dict = {"title": goal[1], "duration": goal[2], "timeDone": goal[3], "date": goal[4]}

        dict_list.append(goal_dict)

    return dict_list

def get_todays_goals_from_database_as_dicts(user_id):
    goals = get_goals_from_database_as_dicts(user_id)
    todays_date = get_current_iso_date()

    todays_goals = []
    for goal in goals:
        if (goal["date"] == todays_date):
            todays_goals.append(goal)

    return todays_goals