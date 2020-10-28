import datetime


class LightState:
    __instance = None
    API_KEY = None
    ALARM_START_TIME = datetime.time(7, 30, 0)
    ALARM_STOP_TIME = datetime.time(7, 50, 0)
    ALARM_CURRENT_STATE = 0

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
