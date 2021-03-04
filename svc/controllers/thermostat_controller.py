import json

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.services import temperature
from svc.utilities.conversion_utils import convert_to_celsius, convert_to_fahrenheit
from svc.utilities.file_utils import write_desired_temp_to_file, get_desired_temp
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
    write_desired_temp_to_file(temp, json_request['mode'])


def __create_response(internal_temp, is_fahren, weather_data):
    state = get_desired_temp()
    desired_temp = __convert_desired_temp(is_fahren, internal_temp, state)
    response = {'currentTemp': internal_temp, 'isFahrenheit': is_fahren,
                'minThermostatTemp': 50.0 if is_fahren else 10.0,
                'maxThermostatTemp': 90.0 if is_fahren else 32.0,
                'mode': state['mode'], 'desiredTemp': desired_temp}
    response.update(weather_data)
    return response


def __convert_desired_temp(is_fahren, internal_temp, state):
    desired_temp = state['desiredTemp']
    if desired_temp is None:
        return internal_temp
    elif is_fahren:
        return convert_to_fahrenheit(desired_temp)
    else:
        return desired_temp
