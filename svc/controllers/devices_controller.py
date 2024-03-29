from werkzeug.exceptions import BadRequest

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.jwt_utils import is_jwt_valid


def add_device_to_role(bearer_token, user_id, request_data):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        try:
            return database.add_new_role_device(user_id, request_data['roleName'], request_data['ipAddress'])
        except KeyError:
            raise BadRequest


def add_node_to_device(bearer_token, user_id, device_id, request_data):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        try:
            return database.add_new_device_node(user_id, device_id, request_data['nodeName'], request_data.get('preferred'))
        except KeyError:
            raise BadRequest
