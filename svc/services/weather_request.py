import logging

from requests.exceptions import ConnectionError

from svc.constants.weather import WEATHER
from svc.models.thermostat import DailyForecast
from svc.utilities.api_utils import get_city_coordinates, get_forecast_by_coords


def get_weather(city, unit, state=None):
    try:
        city = get_city_coordinates(city, state)
        coords = city.get('results', [])[0]
        forecast = get_forecast_by_coords(coords['latitude'], coords['longitude'], unit)
        return __build_response(forecast)
    except (ConnectionError, KeyError, IndexError):
        logging.info('Weather API connection error!')
        return __build_response({})


def __build_response(daily_forecast):
    daily = daily_forecast.get('daily', {})
    current = daily_forecast.get('current_weather', {})
    current_temp = current.get('temperature', 0.0)
    code = current.get('weathercode', 0)
    description = WEATHER.get(code)
    min_temp = daily.get('temperature_2m_min', [0.0])[0]
    max_temp = daily.get('temperature_2m_max', [0.0])[0]

    return DailyForecast(temp=current_temp, minTemp=min_temp, maxTemp=max_temp, description=description)
