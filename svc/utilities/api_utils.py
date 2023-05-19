import json

import requests
from werkzeug.exceptions import FailedDependency, BadRequest, Unauthorized

from svc.constants.settings_state import Settings

# TODO: move to settings file
LIGHT_BASE_URL = 'http://127.0.0.1:5002/lights'
# LIGHT_BASE_URL = 'http://192.168.1.142:80/api'
SMTP_URL = 'https://api.sendinblue.com/v3/smtp/email'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5'


def get_weather_by_city(city, unit, app_id):
    args = {'q': city, 'units': unit, 'APPID': app_id}
    response = requests.get(f'{WEATHER_URL}/weather', params=args)
    __validate_response(response)
    return response.json()


def get_forecast_by_coords(coords, unit, app_id):
    args = {'lat': coords['lat'], 'lon': coords['lon'], 'units': unit, 'appid': app_id, 'exclude': 'alerts,current,hourly,minutely'}
    response = requests.get(f'{WEATHER_URL}/onecall', params=args)
    __validate_response(response)
    return response.json()


def get_garage_door_status(bearer_token, base_url, garage_id):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = f'{base_url}/garageDoor/{garage_id}/status'
    try:
        response = requests.get(url, headers=header, timeout=5)
    except Exception:
        raise FailedDependency()
    __validate_garage_response(response)
    return response.json()


def toggle_garage_door_state(bearer_token, base_url, garage_id):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = f'{base_url}/garageDoor/{garage_id}/toggle'
    try:
        response = requests.get(url, headers=header, timeout=5)
    except Exception:
        raise BadRequest(description='Garage node returned a failure')
    __validate_garage_response(response)


def update_garage_door_state(bearer_token, base_url, garage_id, request):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = f'{base_url}/garageDoor/{garage_id}/state'
    try:
        response = requests.post(url, headers=header, data=request, timeout=5)
    except Exception:
        raise BadRequest(description='Garage node returned a failure')
    __validate_garage_response(response)
    return response.json()


def get_light_groups():
    url = f'{LIGHT_BASE_URL}/groups'
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        raise FailedDependency()
    __validate_response(response)
    return response.json()


def set_light_groups(group_id, on, brightness):
    url = f'{LIGHT_BASE_URL}/group/state'
    state = False if brightness == 0 else on
    request = {'groupId': group_id, 'on': state}
    if brightness != 0 and brightness is not None:
        request['brightness'] = brightness

    __validate_response(requests.post(url, data=json.dumps(request)))


def create_light_group(group_name):
    url = f'{LIGHT_BASE_URL}/group/create'
    request = {'name': group_name}
    requests.post(url, data=json.dumps(request))


def delete_light_group(group_id):
    url = f'{LIGHT_BASE_URL}/group/{group_id}'
    requests.delete(url)


def set_light_state(light_id, brightness):
    url = f'{LIGHT_BASE_URL}/light/state'
    request = {'lightId': light_id, 'on': False if brightness == 0 else True}
    if brightness != 0:
        request['brightness'] = brightness

    __validate_response(requests.post(url, data=json.dumps(request)))


def send_new_account_email(email, password):
    settings = Settings.get_instance()
    headers = {
        'api-key': settings.email_app_id,
        'content-type': 'application/json',
        'accept': 'application/json'}
    request = {
        'sender': {'name': 'Home Automation', 'email': 'senderalex@example.com'},
        'to': [{'email': email, 'name': 'Your Name'}],
        'subject': 'Home Automation: New Account Registration',
        'htmlContent': f'<html><head></head><body><p>Hello,</p><p>A new Home Automation account has been setup for you.</p><p>Password: {password}</p></body></html>'
    }
    requests.post(SMTP_URL, data=json.dumps(request), headers=headers)


def __validate_response(response):
    if response.status_code == 401:
        raise Unauthorized()
    if response.status_code > 299:
        raise FailedDependency()


def __validate_garage_response(response):
    if response.status_code > 299:
        raise BadRequest(description='Garage node returned a failure')
