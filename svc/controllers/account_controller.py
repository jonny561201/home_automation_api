from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.credential_repository import CredentialRepository
from svc.utilities.api_utils import send_new_account_email
from svc.utilities.string_utils import generate_password
from svc.utilities.jwt_utils import AuthClient


def change_password(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with CredentialRepository() as database:
        database.change_user_password(user_id, request_data['oldPassword'], request_data['newPassword'])


def create_child_account_by_user(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    email = request_data.get('email')
    roles = request_data.get('roles')
    # if email == '' or roles == []:
    #     raise BadRequest()
    # new_pass = generate_password(10)
    with AccountRepository() as database:
        child_account = database.create_child_account(user_id, email)
    # send_new_account_email(request_data['email'], new_pass)
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