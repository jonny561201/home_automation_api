import json

from svc.constants.hvac_state import HvacState
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.services import temperature
from svc.utilities.conversion_utils import convert_to_celsius, convert_to_fahrenheit
from svc.utilities.event_utils import create_thread
from svc.utilities.hvac_utils import run_temperature_program
from svc.utilities.jwt_utils import is_jwt_valid


def get_user_temp(user_id, bearer_token):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        preference = database.get_preferences_by_user(user_id)
        internal_temp = temperature.get_internal_temp(preference)
        weather_data = temperature.get_external_temp(preference)

        return __create_response(internal_temp, preference['is_fahrenheit'], weather_data)


def set_user_temperature(request, bearer_token):
    is_jwt_valid(bearer_token)
    json_request = json.loads(request.decode('UTF-8'))
    temp = json_request['desiredTemp'] if not json_request['isFahrenheit'] else convert_to_celsius(json_request['desiredTemp'])
    __create_hvac_thread(temp, json_request)


def __create_response(internal_temp, is_fahren, weather_data):
    state = HvacState.get_instance()
    desired_temp = __convert_desired_temp(is_fahren, internal_temp, state)
    response = {'currentTemp': internal_temp, 'isFahrenheit': is_fahren,
                'minThermostatTemp': 50.0 if is_fahren else 10.0,
                'maxThermostatTemp': 90.0 if is_fahren else 32.0,
                'mode': state.MODE, 'desiredTemp': desired_temp}
    response.update(weather_data)
    return response


def __convert_desired_temp(is_fahren, internal_temp, state):
    if state.DESIRED_TEMP is None:
        return internal_temp
    elif is_fahren:
        return convert_to_fahrenheit(state.DESIRED_TEMP)
    else:
        return state.DESIRED_TEMP


# Should always set temp to celsius
def __create_hvac_thread(temp, json_request):
    state = HvacState.get_instance()
    if state.ACTIVE_THREAD is None:
        create_thread(state, run_temperature_program)
    state.MODE = json_request['mode']
    state.DESIRED_TEMP = temp
