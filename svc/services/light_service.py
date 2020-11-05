from werkzeug.exceptions import FailedDependency

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightAlarm
from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.api_utils import get_light_api_key
from svc.utilities.event_utils import create_thread
from svc.utilities.light_utils import run_light_program


# TODO: how should I get the devices default user id....would be easier of the database was cloud based...
# loop over this guy to create multiple light alarms
def create_start_light_alarm():
    settings = Settings.get_instance()
    with UserDatabaseManager() as database:
        preference = database.get_preferences_by_user(settings.user_id).get('light_alarm')
    if preference['alarm_time'] is not None and preference['alarm_days'] is not None:
        return create_alarm(settings.light_api_user, settings.light_api_password, preference)


def create_alarm(light_user, light_pass, preference):
    try:
        api_key = get_light_api_key(light_user, light_pass)
        alarm = LightAlarm(preference['alarm_time'], preference['alarm_days'])
        create_thread(alarm, lambda: run_light_program(alarm, api_key, preference['alarm_light_group']), Automation.TIME.TEN_SECONDS)
        return alarm
    except FailedDependency:
        return None
