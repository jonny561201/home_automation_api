import json

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities import jwt_utils
from svc.constants.lights_state import LightState


def get_login(basic_token):
    user_name, pword = jwt_utils.extract_credentials(basic_token)
    with UserDatabaseManager() as user_database:
        user_info = user_database.validate_credentials(user_name, pword)
        return jwt_utils.create_jwt_token(user_info)


def get_user_preferences(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        prefs = database.get_preferences_by_user(user_id)
        prefs.get('light_alarm')['alarm_time'] = str(prefs.get('light_alarm')['alarm_time'])
        return prefs


def save_user_preferences(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    user_preferences = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.insert_preferences_by_user(user_id, user_preferences)
    light_pref = user_preferences.get('lightAlarm')
    LightState.get_instance().add_replace_light_alarm(light_pref.get('alarmLightGroup'), light_pref.get('alarmTime'), light_pref.get('alarmDays'))
