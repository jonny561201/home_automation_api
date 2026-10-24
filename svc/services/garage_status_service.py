from datetime import datetime, timedelta

from svc.services.notification_service import notify_garage_alert


def build_user_doors(raw_doors, info, alert_time_minutes):
    user_doors = [__augment_door(door, info, alert_time_minutes) for door in raw_doors if door['garageId'] in info.nodes]
    for door in user_doors:
        if door['openTooLong']:
            notify_garage_alert(info.id, door['garageId'], door['doorName'], datetime.fromisoformat(door['duration']))
    return user_doors


def __augment_door(door, info, alert_time_minutes):
    node = info.nodes.get(door['garageId'])
    door['doorName'] = node.name
    door['nodeId'] = node.nodeId
    open_too_long = __is_past_alert_time(door, alert_time_minutes)
    door['isPastAlertTime'] = open_too_long
    door['openTooLong'] = open_too_long
    return door


def __is_past_alert_time(door, alert_time_minutes):
    if not door['isGarageOpen'] or alert_time_minutes <= 0:
        return False
    duration = datetime.fromisoformat(door['duration'])
    return datetime.now(tz=duration.tzinfo) - duration > timedelta(minutes=alert_time_minutes)
