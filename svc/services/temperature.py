from svc.constants.settings_state import Settings
from svc.services.weather_request import get_weather
from svc.utilities.file_utils import read_temperature_file
from svc.utilities.user_temp_utils import get_user_temperature


def get_external_temp(preference):
    temp_unit = "metric" if preference['temp_unit'] == "celsius" else "imperial"
    settings = Settings.get_instance()
    return get_weather(preference['city'], temp_unit, settings.weather_app_id)


def get_internal_temp(preference):
    temp_text = read_temperature_file()
    return get_user_temperature(temp_text, preference['is_fahrenheit'])
