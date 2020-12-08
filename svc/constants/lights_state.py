import datetime


# TODO: have light state replace existing light alarm by group id
# TODO: have light state cancel alarm by group id
class LightState:
    __instance = None
    API_KEY = None
    LIGHT_ALARMS = []

    def __init__(self):
        if LightState.__instance is not None:
            raise Exception
        else:
            LightState.__instance = self

    def add_light_alarm(self, alarm_time, alarm_days, light_group_id):
        alarm = LightAlarm(alarm_time, alarm_days)
        alarm.LIGHT_GROUP_ID = light_group_id
        self.LIGHT_ALARMS.append(alarm)

    @staticmethod
    def get_instance():
        if LightState.__instance is None:
            LightState.__instance = LightState()
        return LightState.__instance


class LightAlarm:
    ALARM_COUNTER = 0
    ACTIVE_THREAD = None
    STOP_EVENT = None
    ALARM_START_TIME = None
    ALARM_STOP_TIME = None
    ALARM_DAYS = None
    LIGHT_GROUP_ID = None

    def __init__(self, alarm_time, alarm_days):
        self.ALARM_DAYS = alarm_days
        self.ALARM_START_TIME = (datetime.datetime.combine(datetime.date.today(), alarm_time) + datetime.timedelta(minutes=-10)).time()
        self.ALARM_STOP_TIME = (datetime.datetime.combine(datetime.date.today(), alarm_time) + datetime.timedelta(minutes=+10)).time()
