import base64
import json

import requests
from werkzeug.exceptions import FailedDependency, BadRequest

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings

# TODO: move to settings file
LIGHT_BASE_URL = 'http://192.168.1.142:80/api'
SMTP_URL = 'https://api.sendinblue.com/v3/smtp/email'
WEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


def get_weather_by_city(city, unit, app_id):
    args = {'q': city, 'units': unit, 'APPID': app_id}
    response = requests.get(WEATHER_URL, params=args)
    return response.status_code, response.content


def get_garage_door_status(bearer_token, base_url, garage_id):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = '%s/garageDoor/%s/status' % (base_url, garage_id)
    try:
        response = requests.get(url, headers=header, timeout=5)
    except Exception:
        raise FailedDependency()
    __validate_garage_response(response)
    return response.json()


def toggle_garage_door_state(bearer_token, base_url, garage_id):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = '%s/garageDoor/%s/toggle' % (base_url, garage_id)
    try:
        response = requests.get(url, headers=header, timeout=5)
    except Exception:
        raise BadRequest(description='Garage node returned a failure')
    __validate_garage_response(response)


def update_garage_door_state(bearer_token, base_url, garage_id, request):
    header = {'Authorization': 'Bearer ' + bearer_token}
    url = '%s/garageDoor/%s/state' % (base_url, garage_id)
    try:
        response = requests.post(url, headers=header, data=request, timeout=5)
    except Exception:
        raise BadRequest(description='Garage node returned a failure')
    __validate_garage_response(response)
    return response.json()


def get_light_api_key(username, password):
    body = {'devicetype': Automation().APP_NAME}
    auth = base64.b64encode((username + ':' + password).encode('UTF-8')).decode('UTF-8')
    headers = {'Authorization': 'Basic ' + auth}
    try:
        response = requests.post(LIGHT_BASE_URL, data=json.dumps(body), headers=headers, timeout=5)
        api_key = response.json()[0]['success']['username']
        return api_key
    except Exception:
        raise FailedDependency()


def get_light_groups(api_key):
    url = LIGHT_BASE_URL + '/%s/groups' % api_key
    try:
        response = requests.get(url)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def set_light_groups(api_key, group_id, brightness):
    url = LIGHT_BASE_URL + '/%s/groups/%s/action' % (api_key, group_id)
    request = {'on': False if brightness == 0 else True}
    if brightness != 0:
        request['bri'] = brightness
        request['ct'] = 2700

    __validate_light_response(requests.put(url, data=json.dumps(request)))


def get_light_group_state(api_key, group_id):
    url = LIGHT_BASE_URL + '/%s/groups/%s' % (api_key, group_id)
    try:
        response = requests.get(url)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def get_light_group_attributes(api_key, group_id):
    url = LIGHT_BASE_URL + '/%s/groups/%s' % (api_key, group_id)
    try:
        response = requests.get(url)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def create_light_group(api_key, group_name):
    url = LIGHT_BASE_URL + '/%s/groups' % api_key
    request = {'name': group_name}
    requests.post(url, data=json.dumps(request))


def get_all_lights(api_key):
    url = LIGHT_BASE_URL + '/%s/lights' % api_key
    try:
        response = requests.get(url)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def get_light_state(api_key, light_id):
    url = LIGHT_BASE_URL + '/%s/lights/%s' % (api_key, light_id)
    try:
        response = requests.get(url)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def set_light_state(api_key, light_id, brightness):
    url = LIGHT_BASE_URL + '/%s/lights/%s/state' % (api_key, light_id)
    request = {'on': False if brightness == 0 else True}
    if brightness != 0:
        request['bri'] = brightness
        request['ct'] = 2700

    __validate_light_response(requests.put(url, data=json.dumps(request)))


def get_full_state(api_key):
    url = LIGHT_BASE_URL + '/%s' % api_key
    try:
        response = requests.get(url, timeout=10)
    except Exception:
        raise FailedDependency()
    __validate_light_response(response)
    return response.json()


def send_new_account_email(email, password):
    settings = Settings.get_instance()
    headers = {
        'api-key': settings.email_app_id,
        'content-type': 'application/json'}
    request = {
        "sender": {"name": "My Name", "email": email},
        "to": [{"email": email, "name": "My Name"}],
        "subject": "Home Automation: New Account Registration",
        "htmlContent": "<html><head></head><body><p>Hello,</p><p>A new Home Automation account has been setup for you.</p><p>Password: %s</p></body></html>" % password
    }
    requests.post(SMTP_URL, data=json.dumps(request), headers=headers)


def __validate_light_response(response):
    if response.status_code > 299:
        raise FailedDependency()


def __validate_garage_response(response):
    if response.status_code > 299:
        raise BadRequest(description='Garage node returned a failure')
