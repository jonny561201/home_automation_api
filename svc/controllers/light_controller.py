import os

from svc.constants.settings_state import Settings
from svc.utilities import api_utils
from svc.services.light_mapper import map_light_groups
from svc.utilities.jwt_utils import is_jwt_valid


def get_assigned_lights(bearer_token):
    is_jwt_valid(bearer_token)
    settings = Settings.get_instance().get_settings()
    username = settings.get('LightApiUser') if settings.get('Development') else os.environ['LIGHT_API_USERNAME']
    password = settings.get('LightApiPass') if settings.get('Development') else os.environ['LIGHT_API_PASSWORD']
    api_key = api_utils.get_light_api_key(username, password)

    light_groups = api_utils.get_light_groups(api_key)
    groups_state = __get_light_group_states(api_key, light_groups)

    return map_light_groups(light_groups, groups_state)


def __get_light_group_states(api_key, light_groups):
    groups_state = {k: api_utils.get_light_group_state(api_key, k) for k, v in light_groups.items()}
    return groups_state