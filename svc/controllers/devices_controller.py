from werkzeug.exceptions import BadRequest

from svc.utilities.jwt_utils import is_jwt_valid
from svc.db.methods.user_credentials import UserDatabaseManager


def add_device_to_role(bearer_token, request_data):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        try:
            database.add_new_role_device(request_data['userId'], request_data['roleName'], request_data['ipAddress'])
        except KeyError:
            raise BadRequest
