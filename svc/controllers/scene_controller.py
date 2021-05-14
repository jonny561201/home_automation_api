from svc.utilities.jwt_utils import is_jwt_valid


def get_created_scenes(bearer_token):
    is_jwt_valid(bearer_token)