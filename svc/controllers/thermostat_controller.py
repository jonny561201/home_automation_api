import json

from svc.constants.home_automation import Automation
from svc.db.repositories.account_repository import AccountRepository
from svc.models.thermostat import ThermostatState
from svc.services import weather_request
from svc.utilities.conversion_utils import convert_to_celsius, convert_to_fahrenheit
from svc.utilities.file_utils import write_desired_temp_to_file, get_desired_temp, read_temperature_file
from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.rabbitmq_client import publish
from svc.utilities.user_temp_utils import get_user_temperature


def get_user_temp(user_id, bearer_token):
    is_jwt_valid(bearer_token)
    with AccountRepository() as database:
        preference = database.get_preferences_by_user(user_id)
        temp_text = read_temperature_file()
        internal_temp = get_user_temperature(temp_text, preference.isFahrenheit)

        return __create_response(internal_temp, preference.isFahrenheit)


#TODO: update database account repo to store lat/lon of city
def get_user_forecast(user_id, bearer_token):
    is_jwt_valid(bearer_token)
    with AccountRepository() as database:
        preference = database.get_preferences_by_user(user_id)
        return weather_request.get_weather(preference.city, preference.tempUnit)


def set_user_temperature(request, bearer_token):
    is_jwt_valid(bearer_token)
    json_request = json.loads(request.decode('UTF-8'))
    temp = json_request['desiredTemp'] if not json_request['isFahrenheit'] else convert_to_celsius(json_request['desiredTemp'])
    mode = json_request['mode']
    write_desired_temp_to_file(temp, mode)
    publish(Automation.HVAC.QUEUE, {'desiredTemp': temp, 'mode': mode, 'isAuto': mode == 'auto'})


def __create_response(internal_temp, is_fahren):
    state = get_desired_temp()
    desired_temp = __convert_desired_temp(is_fahren, internal_temp, state)
    return ThermostatState(
        currentTemp=internal_temp,
        isFahrenheit=is_fahren,
        minThermostatTemp=50.0 if is_fahren else 10.0,
        maxThermostatTemp=90.0 if is_fahren else 32.0,
        mode=state['mode'],
        desiredTemp=desired_temp
    )


def __convert_desired_temp(is_fahren, internal_temp, state):
    desired_temp = state.get('desiredTemp')
    if desired_temp is None:
        return internal_temp
    elif is_fahren:
        return convert_to_fahrenheit(desired_temp)
    else:
        return desired_temp
