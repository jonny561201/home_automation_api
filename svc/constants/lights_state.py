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
    THREAD_EVENT = None
    ALARM_START_TIME = None
    ALARM_STOP_TIME = None

    def __init__(self, event, start_time, stop_time):
        self.THREAD_EVENT = event
        self.ALARM_START_TIME = datetime.time(12, 2, 0)
        self.ALARM_STOP_TIME = datetime.time(12, 22, 0)
