import sqlite3
from ..utils.dates import get_current_iso_date, get_yesterdays_iso_date
import bcrypt

def get_streak(user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    res = cur.execute("SELECT Streak FROM User WHERE UserID = ?;", (user_id,))
    streak_tuple = res.fetchone()

    if (streak_tuple == None):
        return None
    else:
        return streak_tuple[0]
    
def update_streak(user_id):

    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get the current date
    current_date = get_current_iso_date()

    # Get the user's current streak
    current_streak = get_streak(user_id)

    # First check if the user hasn't already had the streak updated
    res = cur.execute("SELECT * FROM User JOIN Activity ON User.UserID = Activity.UserID WHERE User.UserID = ? AND Date = ?;", (user_id, current_date))
    if (len(res.fetchall()) >= 2 and current_streak != 0):
        # Streak has already been updated, so do nothing
        return current_streak

    # Get the user's new streak
    new_streak = current_streak + 1

    # Update the database
    res = cur.execute("UPDATE User SET Streak = ? WHERE UserID = ?;", (new_streak, user_id))

    # Close the database
    con.commit()
    con.close()

    # Return the new streak
    return new_streak

# On loading the web app, reset the streak if they didn't do anything on the previous day
def reset_streak_if_expired(user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get yesterday's date and today's date in ISO format
    yesterdays_date = get_yesterdays_iso_date()
    todays_date = get_current_iso_date()

    # Check if the user has any activities with yesterday's date
    res = cur.execute("SELECT * FROM Activity WHERE UserID = ? AND Date = ?;", (user_id, yesterdays_date))

    # Get the records from the query
    records = res.fetchall()
    no_activities_on_previous_day = len(records) == 0

    # Check if the user has any activities with today's date
    res = cur.execute("SELECT * FROM Activity WHERE UserID = ? AND Date = ?;", (user_id, todays_date))

    # Get the records from the query
    records = res.fetchall()
    no_activities_on_current_day = len(records) == 0

    if (no_activities_on_previous_day and no_activities_on_current_day):
        # User recorded no activities yesterday so remove their streak
        res = cur.execute("UPDATE User SET Streak = 0 WHERE UserID = ?;", (user_id,))

    # Write changes
    con.commit()
    con.close()

    # Return the streak
    return get_streak(user_id)


def get_email_address_from_user_id(user_id):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get email address from the User table
    res = cur.execute("SELECT Email FROM User WHERE UserID = ?", (user_id,))
    con.commit()

    email_tuple = res.fetchone()
    if (email_tuple == None):
        return None
    else:
        return email_tuple[0]
    

def delete_account(user_id):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Delete all activities associated with the user
    cur.execute("DELETE FROM Activity WHERE UserID = ?", (user_id,))

    # Delete all scheduled activities associated with the user
    cur.execute("DELETE FROM ScheduledActivity WHERE UserID = ?", (user_id,))

    # Delete all goals associated with the user
    cur.execute("DELETE FROM Goal WHERE UserID = ?", (user_id,))

    # Delete the user from the User table
    cur.execute("DELETE FROM User WHERE UserID = ?", (user_id,))

    # Write changes to the database
    con.commit()
    con.close()

def update_email_address(user_id, new_email_address):
    # Connect to the database
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Update the email address in the User table
    cur.execute("UPDATE User SET Email = ? WHERE UserID = ?", (new_email_address, user_id))

    # Write changes to the database
    con.commit()
    con.close()

# Inserts a new user into the User table and returns the UserID
def insert_user(email_address, hashed_password):
    # Create a new User in the User table
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    cur.execute("INSERT INTO User (Email, PasswordHash, Streak) VALUES (?, ?, ?)", (email_address, hashed_password, 0))
    con.commit()

    # Get the UserID of the newly created user
    res = cur.execute("SELECT UserID FROM User WHERE Email = ?", (email_address,))
    user_id = res.fetchone()[0]

    con.close()

    return user_id

# Returns the UserID of the user with a given email, and -1 otherwise
def check_login(email_address, password):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    # Get the password hash from the user with the given email address
    res = cur.execute("SELECT * FROM User WHERE Email = ?", (email_address,))
    record = res.fetchone()
    con.commit()
    con.close()

    if (record == None):
        # User with the given email address does not exist
        return -1
    
    # Check if the password matches the hashed password
    stored_password_hash = record[2]

    if (not bcrypt.checkpw(password.encode("utf-8"), stored_password_hash.encode("utf-8"))):
        # Passwords do not match
        return -1
    
    # Return the UserID
    return record[0]
    
def email_exists_in_database(email_address):
    con = sqlite3.connect("timeaudit.db")
    cur = con.cursor()

    res = cur.execute("SELECT * FROM User WHERE Email = ?", (email_address,))
    record = res.fetchone()

    con.commit()
    con.close()

    if (record == None):
        # Email is not in the database
        return False
    else: 
        return True