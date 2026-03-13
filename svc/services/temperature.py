from svc.services.weather_request import get_weather
from svc.utilities.file_utils import read_temperature_file
from svc.utilities.user_temp_utils import get_user_temperature


def get_external_temp(preference):
    return get_weather(preference.city, preference.tempUnit)


def get_internal_temp(preference):
    temp_text = read_temperature_file()
    return get_user_temperature(temp_text, preference.isFahrenheit)
