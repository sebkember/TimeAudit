import datetime

def get_current_iso_date():
    return datetime.datetime.now().isoformat().split("T")[0]

def get_yesterdays_iso_date():
    yesterdays_date = datetime.datetime.now() - datetime.timedelta(1)
    return yesterdays_date.isoformat().split("T")[0]

def get_iso_date_from__datetime(dt):
    return dt.isoformat().split("T")[0]