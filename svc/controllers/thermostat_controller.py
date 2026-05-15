from svc.db.repositories.tasks_repository import TasksRepository
from svc.db.repositories.user_repository import UserRepository
from svc.constants.home_automation import Automation, AuthClaims
from svc.services import thermostat_service
from svc.utilities.conversion_utils import convert_to_celsius
from svc.utilities.file_utils import write_desired_temp_to_file, read_temperature_file
from svc.utilities.auth_utils import AuthClient
from svc.utilities.rabbitmq_client import publish
from svc.utilities.timezone_utils import resolve_timezone
from svc.utilities.user_temp_utils import get_user_temperature


def get_user_temp(bearer_token, timezone_header=None):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        preference = database.get_preferences_by_user(user_id)
    with TasksRepository() as database:
        tasks = database.get_schedule_tasks_by_user(user_id, 'hvac')
    temp_text = read_temperature_file()
    is_fahrenheit = preference.tempUnit == 'fahrenheit'
    internal_temp = get_user_temperature(temp_text, is_fahrenheit)
    tz = resolve_timezone(timezone_header)

    return thermostat_service.build_thermostat_state(internal_temp, is_fahrenheit, tasks.tasks, tz)


def get_user_forecast(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        preference = database.get_preferences_by_user(user_id)
    return thermostat_service.get_forecast_for_preference(preference)


def get_user_extended_forecast(bearer_token, timezone_header=None):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        preference = database.get_preferences_by_user(user_id)
    tz = resolve_timezone(timezone_header)
    return thermostat_service.get_extended_forecast_for_preference(preference, tz)


def set_user_temperature(request_data, bearer_token):
    AuthClient.get_instance().verify_jwt(bearer_token)
    temp = request_data['desiredTemp'] if not request_data['isFahrenheit'] else convert_to_celsius(request_data['desiredTemp'])
    mode = request_data['mode']
    write_desired_temp_to_file(temp, mode)
    publish(Automation.HVAC.QUEUE, {'desiredTemp': temp, 'mode': mode, 'isAuto': mode == 'auto'})
