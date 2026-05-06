from requests.exceptions import ConnectionError

from svc.constants.weather import WEATHER
from svc.models.thermostat import DailyForecast
from svc.utilities.api_utils import get_city_coordinates, get_forecast_by_coords


def get_weather_by_coords(latitude, longitude, unit):
    return __forecast_for_coords(latitude, longitude, unit)


def get_weather_by_city(city, unit, state=None):
    try:
        geocode = get_city_coordinates(city, state)
        coords = geocode.get('results', [])[0]
    except (ConnectionError, KeyError, IndexError):
        return __build_response({})
    return __forecast_for_coords(coords['latitude'], coords['longitude'], unit)


def __forecast_for_coords(latitude, longitude, unit):
    try:
        forecast = get_forecast_by_coords(latitude, longitude, unit)
    except ConnectionError:
        return __build_response({})
    return __build_response(forecast)


def __build_response(daily_forecast):
    daily = daily_forecast.get('daily', {})
    current = daily_forecast.get('current_weather', {})
    current_temp = current.get('temperature', 0.0)
    code = current.get('weathercode', 0)
    description = WEATHER.get(code)
    min_temp = daily.get('temperature_2m_min', [0.0])[0]
    max_temp = daily.get('temperature_2m_max', [0.0])[0]

    return DailyForecast(temp=current_temp, minTemp=min_temp, maxTemp=max_temp, description=description)
