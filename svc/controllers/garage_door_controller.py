from svc.utilities.jwt_utils import is_jwt_valid


def get_status(bearer_token):
    is_jwt_valid(bearer_token)


def update_state(bearer_token, request):
    is_jwt_valid(bearer_token)


def toggle_door(bearer_token):
    is_jwt_valid(bearer_token)
