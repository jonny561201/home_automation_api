from werkzeug.exceptions import BadRequest

from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.credential_repository import CredentialRepository
from svc.utilities import jwt_utils
from svc.utilities.api_utils import send_new_account_email
from svc.utilities.string_utils import generate_password


def change_password(bearer_token, request_data):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    with CredentialRepository() as database:
        database.change_user_password(user_id, request_data['oldPassword'], request_data['newPassword'])


def get_roles(bearer_token):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    with AccountRepository() as database:
        return database.get_roles_by_user(user_id)


def get_roles_v2(bearer_token):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    with AccountRepository() as database:
        return database.get_user_roles(user_id)


def create_child_account_by_user(bearer_token, request_data):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    email = request_data.get('email')
    roles = request_data.get('roles')
    if email == '' or roles == []:
        raise BadRequest()
    new_pass = generate_password(10)
    with AccountRepository() as database:
        child_accounts = database.create_child_account(user_id, email, roles, new_pass)
    send_new_account_email(request_data['email'], new_pass)
    return child_accounts


def get_child_accounts_by_user(bearer_token):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    with AccountRepository() as database:
        return database.get_user_child_accounts(user_id)


def delete_child_account(bearer_token, child_user_id):
    claims = jwt_utils.is_jwt_valid(bearer_token)
    user_id = claims['sub']
    with AccountRepository() as database:
        database.delete_child_user_account(user_id, child_user_id)