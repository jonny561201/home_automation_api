from svc.models.thermostat import ThermostatState
from svc.services import weather_request
from svc.utilities.conversion_utils import convert_to_fahrenheit
from svc.utilities.file_utils import get_desired_temp


def build_thermostat_state(internal_temp, is_fahrenheit):
    state = get_desired_temp()
    desired_temp = __convert_desired_temp(is_fahrenheit, internal_temp, state)
    return ThermostatState(
        currentTemp=internal_temp,
        isFahrenheit=is_fahrenheit,
        minThermostatTemp=50.0 if is_fahrenheit else 10.0,
        maxThermostatTemp=90.0 if is_fahrenheit else 32.0,
        mode=state['mode'],
        desiredTemp=desired_temp
    )


def get_forecast_for_preference(preference):
    if preference.latitude != None and preference.longitude != None:
        return weather_request.get_weather_by_coords(preference.latitude, preference.longitude, preference.tempUnit)
    return weather_request.get_weather_by_city(preference.city, preference.tempUnit, preference.state)


def get_extended_forecast_for_preference(preference):
    if preference.latitude != None and preference.longitude != None:
        return weather_request.get_extended_weather_by_coords(preference.latitude, preference.longitude, preference.tempUnit)
    return weather_request.get_extended_weather_by_city(preference.city, preference.tempUnit, preference.state)


def __convert_desired_temp(is_fahrenheit, internal_temp, state):
    desired_temp = state.get('desiredTemp')
    if desired_temp is None:
        return internal_temp
    elif is_fahrenheit:
        return convert_to_fahrenheit(desired_temp)
    else:
        return desired_temp
