import requests
from werkzeug.exceptions import FailedDependency, BadRequest, Unauthorized

from svc.config.settings_state import Settings
from svc.utilities.string_utils import generate_password


def get_city_coordinates(city):
    args = {'name': city, 'count': 1}
    base_url = Settings.get_instance().BaseUrls.weather
    response = requests.get(f'https://geocoding-{base_url}/search', params=args)
    __validate_response(response)
    return response.json()


def get_forecast_by_coords(lat, lon, unit):
    args = {
        'latitude': lat,
        'longitude': lon,
        'current_weather': True,
        'temperature_unit': unit,
        'daily': 'temperature_2m_max,temperature_2m_min,weathercode',
        'forecast_days': 1,
        'timezone': 'auto'
    }
    base_url = Settings.get_instance().BaseUrls.weather
    response = requests.get(f'https://{base_url}/forecast', params=args)
    __validate_response(response)
    return response.json()


def get_garage_door_status(api_key, base_url, garage_id):
    header = {'X-API-Key': api_key}
    try:
        response = requests.get(f'{base_url}/garageDoor/{garage_id}/status', headers=header, timeout=5)
    except Exception:
        raise FailedDependency()
    __validate_garage_response(response)
    return response.json()


def get_all_garage_doors_status(api_key, base_url):
    header = {'X-API-Key': api_key}
    try:
        response = requests.get(f'{base_url}/garageDoor/status', headers=header, timeout=5)
    except Exception:
        raise FailedDependency()
    __validate_garage_response(response)
    return response.json()


def register_garage_device(ip, port):
    try:
        response = requests.post(f'http://{ip}:{port}/register', timeout=5)
    except Exception:
        raise FailedDependency()
    __validate_response(response)
    return response.json()


def get_light_groups(api_key):
    base_url = Settings.get_instance().BaseUrls.lights
    try:
        response = requests.get(f'{base_url}/groups', headers={'LightApiKey': api_key}, timeout=10)
    except Exception:
        raise FailedDependency()
    __validate_response(response)
    return response.json()


def set_light_groups(api_key, group_id, on, brightness):
    base_url = Settings.get_instance().BaseUrls.lights
    state = False if brightness == 0 else on
    request = {'groupId': group_id, 'on': state}
    if brightness != 0 and brightness is not None:
        request['brightness'] = brightness

    __validate_response(requests.post(f'{base_url}/group/state', json=request, headers={'LightApiKey': api_key}))


def create_light_group(api_key, group_name):
    base_url = Settings.get_instance().BaseUrls.lights

    request = {'name': group_name}
    requests.post(f'{base_url}/group/create', json=request, headers={'LightApiKey': api_key})


def delete_light_group(group_id):
    base_url = Settings.get_instance().BaseUrls.lights

    requests.delete(f'{base_url}/group/{group_id}')


def set_light_state(api_key, light_id, brightness):
    base_url = Settings.get_instance().BaseUrls.lights

    request = {'lightId': light_id, 'on': False if brightness == 0 else True, 'brightness': brightness}
    # if brightness != 0:
    #     request['brightness'] = brightness

    __validate_response(requests.post(f'{base_url}/light/state', json=request, headers={'LightApiKey': api_key}))


def get_unregistered_lights(api_key):
    base_url = Settings.get_instance().BaseUrls.lights

    try:
        response = requests.get(f'{base_url}/unregistered', headers={'LightApiKey': api_key}, timeout=10)
        __validate_response(response)
        return response.json()
    except Exception:
        raise FailedDependency()


def assign_light_group(api_key, group_id, light_id, name, switch_type):
    base_url = Settings.get_instance().BaseUrls.lights

    request = {'name': name, 'groupId': group_id, 'lightId': light_id, 'switchTypeId': switch_type}
    requests.post(f'{base_url}/group/assign', json=request, headers={'LightApiKey': api_key})


def exchange_auth0_code(code, code_verifier, redirect_uri):
    settings = Settings.get_instance()
    authority = settings.Authority
    request = {
        'grant_type': 'authorization_code',
        'client_id': authority.client_id,
        'client_secret': authority.client_secret,
        'code': code,
        'code_verifier': code_verifier,
        'redirect_uri': redirect_uri,
    }
    response = requests.post(f'https://{authority.domain}/oauth/token', json=request)
    __validate_response(response)

    return response.json()


def create_auth0_user(email):
    token = __get_management_token()
    authority = Settings.get_instance().Authority
    password = generate_password(24)
    request = {
        'email': email,
        'password': password,
        'email_verified': False,
        'connection': 'Username-Password-Authentication',
    }
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    response = requests.post(f'https://{authority.domain}/api/v2/users', json=request, headers=headers)
    __validate_response(response)
    return response.json()['user_id']


def assign_auth0_roles(auth0_id, role_ids):
    token = __get_management_token()
    authority = Settings.get_instance().Authority
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    request = {'roles': role_ids}
    response = requests.post(f'https://{authority.domain}/api/v2/users/{auth0_id}/roles', json=request, headers=headers)
    __validate_response(response)


def send_auth0_password_reset(email):
    authority = Settings.get_instance().Authority
    request = {
        'client_id': authority.client_id,
        'email': email,
        'connection': 'Username-Password-Authentication',
    }
    response = requests.post(f'https://{authority.domain}/dbconnections/change_password', json=request)
    __validate_response(response)


def __get_management_token():
    authority = Settings.get_instance().Authority
    request = {
        'grant_type': 'client_credentials',
        'client_id': authority.client_id,
        'client_secret': authority.client_secret,
        'audience': f'https://{authority.domain}/api/v2/',
    }
    response = requests.post(f'https://{authority.domain}/oauth/token', json=request)
    __validate_response(response)
    return response.json()['access_token']


def __validate_response(response):
    if response.status_code == 401:
        raise Unauthorized()
    if response.status_code > 299:
        raise FailedDependency()


def __validate_garage_response(response):
    if response.status_code > 299:
        raise BadRequest(description='Garage node returned a failure')
