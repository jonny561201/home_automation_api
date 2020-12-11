from werkzeug.exceptions import FailedDependency

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightState
from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.event_utils import create_thread
from svc.utilities.light_utils import run_light_program


# TODO: how should I get the devices default user id....would be easier if the database was cloud based...
def create_start_light_alarm():
    settings = Settings.get_instance()
    with UserDatabaseManager() as database:
        light_pref = database.get_preferences_by_user(settings.user_id).get('light_alarm')
    if light_pref['alarm_time'] is not None and light_pref['alarm_days'] is not None and light_pref['alarm_light_group'] is not None:
        __create_alarm(light_pref)


def __create_alarm(preference):
    try:
        api_key = LightState.get_instance().get_light_api_key()
        alarm = LightState.get_instance().add_replace_light_alarm(preference['alarm_light_group'], preference['alarm_time'], preference['alarm_days'])
        create_thread(alarm, lambda: run_light_program(alarm, api_key, preference['alarm_light_group']), Automation.TIME.TEN_SECONDS)
    except FailedDependency:
        pass
