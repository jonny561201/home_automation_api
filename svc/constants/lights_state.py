# from svc.constants.settings_state import Settings
# from svc.utilities.api_utils import get_light_api_key
#
#
# class LightState:
#     __instance = None
#     API_KEY = None
#     LIGHT_ALARMS = []
#
#     def __init__(self):
#         if LightState.__instance is not None:
#             raise Exception
#         else:
#             LightState.__instance = self
#
#     def get_light_api_key(self):
#         if self.API_KEY is None:
#             settings = Settings.get_instance()
#             self.API_KEY = get_light_api_key(settings.light_api_user, settings.light_api_password)
#         return self.API_KEY
#
#     @staticmethod
#     def get_instance():
#         if LightState.__instance is None:
#             LightState.__instance = LightState()
#         return LightState.__instance
