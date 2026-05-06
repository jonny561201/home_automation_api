from requests.exceptions import ConnectionError

from svc.constants.weather import WEATHER
from svc.models.thermostat import DailyForecast, ExtendedForecast, ForecastDay
from svc.utilities.api_utils import get_city_coordinates, get_extended_forecast_by_coords, get_forecast_by_coords

DEFAULT_FORECAST_DAYS = 5


def get_weather_by_coords(latitude, longitude, unit):
    return __forecast_for_coords(latitude, longitude, unit)


def get_weather_by_city(city, unit, state=None):
    try:
        geocode = get_city_coordinates(city, state)
        coords = geocode.get('results', [])[0]
    except (ConnectionError, KeyError, IndexError):
        return __build_response({})
    return __forecast_for_coords(coords['latitude'], coords['longitude'], unit)


def get_extended_weather_by_coords(latitude, longitude, unit):
    return __extended_forecast_for_coords(latitude, longitude, unit)


def get_extended_weather_by_city(city, unit, state=None):
    try:
        geocode = get_city_coordinates(city, state)
        coords = geocode.get('results', [])[0]
    except (ConnectionError, KeyError, IndexError):
        return ExtendedForecast(forecast=[])
    return __extended_forecast_for_coords(coords['latitude'], coords['longitude'], unit)


def __forecast_for_coords(latitude, longitude, unit):
    try:
        forecast = get_forecast_by_coords(latitude, longitude, unit)
    except ConnectionError:
        return __build_response({})
    return __build_response(forecast)


def __extended_forecast_for_coords(latitude, longitude, unit):
    try:
        forecast = get_extended_forecast_by_coords(latitude, longitude, unit, DEFAULT_FORECAST_DAYS)
    except ConnectionError:
        return ExtendedForecast(forecast=[])
    return __build_extended_response(forecast)


def __build_response(daily_forecast):
    daily = daily_forecast.get('daily', {})
    current = daily_forecast.get('current_weather', {})
    current_temp = current.get('temperature', 0.0)
    code = current.get('weathercode', 0)
    description = WEATHER.get(code)
    min_temp = daily.get('temperature_2m_min', [0.0])[0]
    max_temp = daily.get('temperature_2m_max', [0.0])[0]

    return DailyForecast(temp=current_temp, minTemp=min_temp, maxTemp=max_temp, description=description)


def __build_extended_response(forecast_payload):
    daily = forecast_payload.get('daily', {})
    dates = daily.get('time', [])
    min_temps = daily.get('temperature_2m_min', [])
    max_temps = daily.get('temperature_2m_max', [])
    codes = daily.get('weathercode', [])

    days = []
    for index, date in enumerate(dates):
        days.append(ForecastDay(
            date=date,
            minTemp=min_temps[index] if index < len(min_temps) else 0.0,
            maxTemp=max_temps[index] if index < len(max_temps) else 0.0,
            description=WEATHER.get(codes[index] if index < len(codes) else 0),
        ))
    return ExtendedForecast(forecast=days)
