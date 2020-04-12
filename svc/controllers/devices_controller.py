from svc.utilities.jwt_utils import is_jwt_valid


def add_device_to_role(bearer_token, request_data):
    is_jwt_valid(bearer_token)
