from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.device_repository import DeviceRepository
from svc.utilities import api_utils
from svc.utilities.auth_utils import AuthClient


def create_child_account_by_user(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    email = request_data.get('email')
    device_ids = request_data.get('deviceIds')

    if not email or not device_ids:
        raise BadRequest()
    with AccountRepository() as database:
        child_account = database.create_child_account(user_id, email, device_ids)
    with DeviceRepository() as database:
        role_ids = database.get_role_ids_by_device_ids(user_id, device_ids)
    _create_auth0_account(email, role_ids)
    return child_account


def get_child_accounts_by_user(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with AccountRepository() as database:
        return database.get_user_child_accounts(user_id)


def delete_child_account(bearer_token, child_user_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with AccountRepository() as database:
        database.delete_child_user_account(user_id, child_user_id)


def _create_auth0_account(email, role_ids):
    auth0_user_id = api_utils.create_auth0_user(email)
    if role_ids:
        api_utils.assign_auth0_roles(auth0_user_id, role_ids)
    api_utils.send_auth0_password_reset(email)