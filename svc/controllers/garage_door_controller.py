from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.user_garage_utils import get_garage_url_by_user


def get_status(bearer_token, user_id):
    is_jwt_valid(bearer_token)


def update_state(bearer_token, user_id, request):
    is_jwt_valid(bearer_token)


def toggle_door(bearer_token, user_id):
    is_jwt_valid(bearer_token)
