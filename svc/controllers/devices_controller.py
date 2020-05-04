from werkzeug.exceptions import BadRequest

from svc.utilities.jwt_utils import is_jwt_valid
from svc.db.methods.user_credentials import UserDatabaseManager


def add_device_to_role(bearer_token, user_id, request_data):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        try:
            return database.add_new_role_device(user_id, request_data['roleName'], request_data['ipAddress'])
        except KeyError:
            raise BadRequest


def add_node_to_device(bearer_token, device_id, request_data):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        try:
            database.add_new_device_node(device_id, request_data['nodeName'])
        except KeyError:
            raise BadRequest
