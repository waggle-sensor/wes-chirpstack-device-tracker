import datetime
import pytz

def epoch_to_UTC(sec: int, nanos: int) -> datetime:
    """
    Convert seconds since epoch to a UTC datetime object
    """
    total_seconds = sec + nanos / 1e9 # Calculate the total seconds with nanoseconds 
    datetime_obj_utc = datetime.datetime.utcfromtimestamp(total_seconds) # Convert seconds since epoch to a datetime object
    return datetime_obj_utc

def UTC_to_Timezone(datetime_obj_utc: datetime ,timezone: str) -> datetime:
    """
    Convert UTC datetime object to a datetime object in the timezone
    datetime_obj_utc: datetime object in utc
    timezone: str acceptable by pytz.timezone()
    """
    timezone_obj = pytz.timezone(timezone)
    # Convert UTC datetime to timezone
    datetime_obj = datetime_obj_utc.replace(tzinfo=pytz.utc).astimezone(timezone_obj)
    return datetime_obj