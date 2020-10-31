from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightAlarm
from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.api_utils import get_light_api_key
from svc.utilities.event_utils import create_thread
from svc.utilities.light_utils import run_light_program


# TODO: how should I get the devices default user id....would be easier of the database was cloud based...
def create_start_light_alarm():
    settings = Settings.get_instance()
    api_key = get_light_api_key(settings.light_api_user, settings.light_api_password)
    with UserDatabaseManager() as database:
        preference = database.get_preferences_by_user(settings.user_id)
    alarm = LightAlarm(preference['alarm_time'], preference['alarm_days'])
    create_thread(alarm, lambda: run_light_program(api_key, preference['alarm_light_group']), Automation.TIME.TEN_SECONDS)
    return alarm
