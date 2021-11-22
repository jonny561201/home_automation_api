import logging

from requests.exceptions import ConnectionError

from svc.utilities.api_utils import get_weather_by_city, get_forecast_by_coords


def get_weather(city, unit, app_id):
    weather = {}
    try:
        weather = get_weather_by_city(city, unit, app_id)
        forecast = get_forecast_by_coords(weather['coord'], unit, app_id)
        daily_forecast = forecast['current']['daily'][0]['temp']
        return __build_response(weather, daily_forecast)
    except (ConnectionError, KeyError, IndexError):
        logging.info('Weather API connection error!')
        return __build_response(weather, {})


def __build_response(weather, daily_forecast):
    main = weather.get('main', {})
    current_temp = main.get('temp', 0.0)
    min_temp = daily_forecast.get('min', 0.0)
    max_temp = daily_forecast.get('max', 0.0)
    forecast_desc = next(iter(weather.get('weather', {})), {}).get('description', '')

    return {'temp': current_temp, 'minTemp': min_temp, 'maxTemp': max_temp, 'description': forecast_desc}
