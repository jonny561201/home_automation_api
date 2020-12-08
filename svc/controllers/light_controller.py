from svc.constants.lights_state import LightState
from svc.utilities import api_utils
from svc.utilities.jwt_utils import is_jwt_valid


def get_assigned_light_groups(bearer_token):
    is_jwt_valid(bearer_token)
    light_state = LightState.get_instance()
    api_key = light_state.get_light_api_key()

    full_state = api_utils.get_full_state(api_key)
    return [__group_mapper(k, v, full_state) for k, v in full_state.get('groups').items()]


def set_assigned_light_groups(bearer_token, request):
    is_jwt_valid(bearer_token)
    light_state = LightState.get_instance()
    api_key = light_state.get_light_api_key()

    api_utils.set_light_groups(api_key, request.get('groupId'), request.get('on'), request.get('brightness'))


def set_assigned_light(bearer_token, request_data):
    is_jwt_valid(bearer_token)
    light_state = LightState.get_instance()
    api_key = light_state.get_light_api_key()

    api_utils.set_light_state(api_key, request_data.get('lightId'), request_data.get('on'), request_data.get('brightness'))


def __group_mapper(k, v, full_state):
    action = v.get('action')
    return {'groupId': k, 'groupName': v.get('name'), 'on': action.get('on'), 'brightness': action.get('bri'),
            'lights': __light_mapper(k, v.get('lights'), full_state.get('lights'))}


def __light_mapper(group_id, group_lights, lights):
    return [{'groupId': group_id, 'lightId': k, 'lightName': v.get('name'), 'on': v.get('state').get('on'), 'brightness': v.get('state').get('bri')}
            for k, v in lights.items() if k in group_lights]

