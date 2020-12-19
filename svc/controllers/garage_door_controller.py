from werkzeug.exceptions import BadRequest

from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.user_garage_utils import get_garage_url_by_user
from svc.utilities import api_utils


def get_status(bearer_token, user_id, garage_id):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    return api_utils.get_garage_door_status(bearer_token, base_url, garage_id)


def update_state(bearer_token, user_id, garage_id, request):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    status, data = api_utils.update_garage_door_state(bearer_token, base_url, garage_id, request)
    __validate_response(status)
    return data


def toggle_door(bearer_token, user_id, garage_id):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    status = api_utils.toggle_garage_door_state(bearer_token, base_url, garage_id)
    __validate_response(status)
    return status


def __validate_response(status):
    if status > 200:
        raise BadRequest(description='Garage node returned a failure')
