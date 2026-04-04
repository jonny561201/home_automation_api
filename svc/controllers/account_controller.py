from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.db.repositories.account_repository import AccountRepository
from svc.utilities.jwt_utils import AuthClient


# TODO: create account and duplicate roles
# TODO: the child will need to signup in auth0
# TODO: then post registration action will need to provision and that needs to check email
def create_child_account_by_user(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    email = request_data.get('email')
    device_ids = request_data.get('deviceIds')

    if email == '' or email is None or device_ids is None or len(device_ids) == 0:
        raise BadRequest()
    with AccountRepository() as database:
        return database.create_child_account(user_id, email, device_ids)


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