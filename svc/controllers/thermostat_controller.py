from werkzeug.exceptions import FailedDependency

from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.tasks_repository import TasksRepository
from svc.db.repositories.user_repository import UserRepository
from svc.constants.home_automation import Automation, AuthClaims
from svc.services import thermostat_service
from svc.utilities import api_utils
from svc.utilities.conversion_utils import convert_to_celsius, convert_to_fahrenheit
from svc.utilities.auth_utils import AuthClient
from svc.utilities.rabbitmq_client import publish
from svc.utilities.timezone_utils import resolve_timezone


def get_user_temp(bearer_token, timezone_header=None):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        preference = database.get_preferences_by_user(user_id)
    with TasksRepository() as database:
        tasks = database.get_schedule_tasks_by_user(user_id, 'hvac')
    with DeviceRepository() as database:
        info = database.get_device_info('thermostat')
    if info is None:
        raise FailedDependency(description="device not registered")
    status = api_utils.get_thermostat_status(info.api_key, f'http://{info.ip_address}:{info.ip_port}')
    is_fahrenheit = preference.tempUnit == 'fahrenheit'
    internal_temp = __to_user_unit(status['currentTemp'], is_fahrenheit)
    tz = resolve_timezone(timezone_header)

    return thermostat_service.build_thermostat_state(internal_temp, status, is_fahrenheit, tasks.tasks, tz)


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
    publish(Automation.HVAC.QUEUE, {'action': 'set', 'desiredTemp': temp, 'mode': mode})


def __to_user_unit(celsius_temp, is_fahrenheit):
    if celsius_temp is None or not is_fahrenheit:
        return celsius_temp
    return convert_to_fahrenheit(celsius_temp)
