class LightState:
    __instance = None
    API_KEY = None
    ALARM_TIME = None
    ALARM_DURATION = 15

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

