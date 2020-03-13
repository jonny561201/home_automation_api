from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.user_garage_utils import get_garage_url_by_user
from svc.utilities import api_utils


def get_status(bearer_token, user_id):
    is_jwt_valid(bearer_token)
    url = get_garage_url_by_user(user_id)
    return api_utils.get_garage_door_status(bearer_token, url)


def update_state(bearer_token, user_id, request):
    is_jwt_valid(bearer_token)
    url = get_garage_url_by_user(user_id)
    api_utils.update_garage_door_state(bearer_token, url, request)


def toggle_door(bearer_token, user_id):
    is_jwt_valid(bearer_token)
    url = get_garage_url_by_user(user_id)
    return api_utils.toggle_garage_door_state(bearer_token, url)
