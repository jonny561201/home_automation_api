import datetime


class LightState:
    __instance = None
    API_KEY = None

    def __init__(self):
        if LightState.__instance is not None:
            raise Exception
        else:
            LightState.__instance = self

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

    def __init__(self, start_time=datetime.time(12, 2, 0), stop_time=datetime.time(12, 22, 0)):
        self.ALARM_START_TIME = start_time
        self.ALARM_STOP_TIME = stop_time
