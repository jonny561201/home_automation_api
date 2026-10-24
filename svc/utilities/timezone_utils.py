from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def resolve_timezone(header_value):
    if header_value is None:
        return ZoneInfo('UTC')
    try:
        return ZoneInfo(header_value)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo('UTC')


def now_in_timezone(tz):
    return datetime.now(tz=tz)


def weekday_label(local_datetime):
    return WEEKDAY_LABELS[local_datetime.weekday()]
