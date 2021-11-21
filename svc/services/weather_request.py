import logging

from requests.exceptions import ConnectionError

from svc.utilities.api_utils import get_weather_by_city


def get_weather(city, unit, app_id):
    response = {}
    try:
        response = get_weather_by_city(city, unit, app_id)
    except ConnectionError:
        logging.info('Weather API connection error!')

    return __build_response(response)


def __build_response(response_content):
    main = response_content.get('main', {})
    current_temp = main.get('temp', 0.0)
    min_temp = main.get('temp_min', 0.0)
    max_temp = main.get('temp_max', 0.0)
    forecast_desc = next(iter(response_content.get('weather', {})), {}).get('description', '')

    return {'temp': current_temp, 'minTemp': min_temp, 'maxTemp': max_temp, 'description': forecast_desc}
