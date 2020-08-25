from datetime import datetime

def get_current_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+02:00")

def get_current_datetime_normal() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
