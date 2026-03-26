import os
from openai import OpenAI
import json
import datetime

from ..db.scheduled_activities import get_scheduled_activities_from_database_as_dicts
from ..db.activities import get_activities_from_database_as_dicts, get_categories
from ..db.goals import get_todays_goals_from_database_as_dicts
from .dates import get_iso_date_from__datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Connect to OpenAI API
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_user_schedule(user_id, date, startTime, endTime): 
    # Get scheduled activities from the database
    scheduled_activities = get_scheduled_activities_from_database_as_dicts(user_id)

    # Get activities from the database
    activities = get_activities_from_database_as_dicts(user_id)

    # Narrow down activities to just those in the past 2 weeks
    iso_two_weeks_ago = get_iso_date_from__datetime(datetime.datetime.now() - datetime.timedelta(weeks=2))

    # Didn't know you could do this lol
    activities = [activity for activity in activities if activity["date"] >= iso_two_weeks_ago]
    scheduled_activities = [activity for activity in scheduled_activities if activity["date"] >= iso_two_weeks_ago]


    # Get goals from the database
    goals = get_todays_goals_from_database_as_dicts(user_id)

    # Get categories from the database
    categories = get_categories()

    # The initial context prompt for the AI
    context_prompt = """
    You are a helpful assistant that creates daily schedules for users based on their goals, past logged activities, and scheduled plans. 
    Generate a schedule for the user on the given date which:
    1. Covers all their goals (e.g. 2hrs revision)
    2. Does not conflict with any activities already scheduled (scheduled_activities) on this date (if an activity is already scheduled, it should NOT be included in the schedule)
    3. Fits in time limits given (in minutes since midnight)
    4. Includes short breaks between activities if possible
    5. Includes activities not in their goals if they are relevant to the user's interests or past activities
    Your output should be a JSON array of activities in the following format:
    { 'title': 'Maths revision', 'category': 'Work/Study', 'startTime': 510, 'endTime': 600, 'date': '2025-08-01' }
    where the 'category' attribute can only be a string from the categories array below, and the 'startTime' and 'endTime' are the times in minutes since midnight on that day.
    DO NOT include any explanatory text, just return the JSON array. DO NOT WRAP THE JSON ARRAY IN ANY OTHER TEXT OR MARKUP.
    """

    prompt_content = json.dumps({
        "date": date,
        "startTime": startTime,
        "endTime": endTime,
        "categories": categories,
        "activities": activities,
        "scheduled_activities": scheduled_activities,
        "goals": goals
    })

    # Create the full prompt 
    prompt = [
        {
            "role": "system",
            "content": context_prompt
        },
        {
            "role": "user",
            "content": prompt_content
        }
    ]

    # Call OpenAI API
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=prompt,
        temperature=0.5,
        top_p=1.0,
        n=1,
        #response_format={"type": "json_array"}
    )

    # Get the generated schedule from the response
    if (response.choices and len(response.choices) > 0):
        return response.choices[0].message.content
    else:
        return []