from werkzeug.exceptions import BadRequest

from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.user_garage_utils import get_garage_url_by_user
from svc.utilities import api_utils


# TODO: check response from api utils to return custom response
def get_status(bearer_token, user_id):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    status, data = api_utils.get_garage_door_status(bearer_token, base_url)
    if status > 200:
        raise BadRequest
    return data


def update_state(bearer_token, user_id, request):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    api_utils.update_garage_door_state(bearer_token, base_url, request)


# TODO: check response from api utils to return custom response
def toggle_door(bearer_token, user_id):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)
    return api_utils.toggle_garage_door_state(bearer_token, base_url)
