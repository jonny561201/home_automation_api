from werkzeug.exceptions import BadRequest

from svc.config.settings_state import Settings
from svc.utilities import api_utils
from svc.utilities.auth_utils import AuthClient


def get_assigned_light_groups(bearer_token):
    AuthClient.get_instance().verify_jwt(bearer_token)
    api_key = Settings.get_instance().light_api_key

    return api_utils.get_light_groups(api_key)


def set_assigned_light_groups(bearer_token, request):
    AuthClient.get_instance().verify_jwt(bearer_token)
    api_key = Settings.get_instance().light_api_key
    try:
        api_utils.set_light_groups(api_key, request['groupId'], request['on'], request.get('brightness'))
    except KeyError:
        raise BadRequest()


def set_assigned_light(bearer_token, request_data):
    AuthClient.get_instance().verify_jwt(bearer_token)
    api_key = Settings.get_instance().light_api_key

    api_utils.set_light_state(api_key, request_data.get('lightId'), request_data.get('brightness'))


def get_unassigned_lights(bearer_token):
    AuthClient.get_instance().verify_jwt(bearer_token)
    api_key = Settings.get_instance().light_api_key

    return api_utils.get_unregistered_lights(api_key)


def register_unassigned_light(bearer_token, request):
    AuthClient.get_instance().verify_jwt(bearer_token)
    name = request.get('name')
    group_id = request.get('groupId')
    light_id = request.get('lightId')
    switch_type_id = request.get('switchTypeId')

    settings = Settings.get_instance()
    api_key = settings.light_api_key
    api_utils.assign_light_group(api_key, group_id, light_id, name, switch_type_id)
