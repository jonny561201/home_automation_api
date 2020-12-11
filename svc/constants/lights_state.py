import datetime

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings
from svc.utilities.api_utils import get_light_api_key
from svc.utilities.event_utils import create_thread
from svc.utilities.light_utils import run_light_program


class LightState:
    __instance = None
    API_KEY = None
    LIGHT_ALARMS = []

    def __init__(self):
        if LightState.__instance is not None:
            raise Exception
        else:
            LightState.__instance = self

    def add_replace_light_alarm(self, light_group_id, alarm_time, alarm_days):
        if light_group_id is None or alarm_time is None:
            return None
        index = next((i for i, x in enumerate(self.LIGHT_ALARMS) if x.LIGHT_GROUP_ID == light_group_id), None)
        if index is not None:
            existing_alarm = self.LIGHT_ALARMS.pop(index)
            existing_alarm.STOP_EVENT.set()
        alarm = LightAlarm(light_group_id, alarm_time, alarm_days)
        create_thread(alarm, lambda: run_light_program(alarm, self.get_light_api_key(), light_group_id), Automation.TIME.TEN_SECONDS)
        self.LIGHT_ALARMS.append(alarm)
        return alarm

    def get_light_api_key(self):
        if self.API_KEY is None:
            settings = Settings.get_instance()
            self.API_KEY = get_light_api_key(settings.light_api_user, settings.light_api_password)
        return self.API_KEY

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

    def __init__(self, light_group_id, alarm_time, alarm_days):
        self.LIGHT_GROUP_ID = light_group_id
        self.ALARM_DAYS = alarm_days
        self.ALARM_START_TIME = (datetime.datetime.combine(datetime.date.today(), alarm_time) + datetime.timedelta(minutes=-10)).time()
        self.ALARM_STOP_TIME = (datetime.datetime.combine(datetime.date.today(), alarm_time) + datetime.timedelta(minutes=+10)).time()
