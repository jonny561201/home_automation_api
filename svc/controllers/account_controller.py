import json

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities import jwt_utils
from svc.utilities.api_utils import send_new_account_email
from svc.utilities.string_utils import generate_password


def change_password(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    request = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.change_user_password(user_id, request['oldPassword'], request['newPassword'])


def get_roles(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_roles_by_user(user_id)


def create_child_account_by_user(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    request = json.loads(request_data.decode('UTF-8'))
    new_pass = generate_password(10)
    with UserDatabaseManager() as database:
        database.create_child_account(user_id, request['email'], request['roles'], new_pass)
    send_new_account_email(request['email'], new_pass)


def get_child_accounts_by_user(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_user_child_accounts(user_id)


def delete_child_account(bearer_token, user_id, child_user_id):
    jwt_utils.is_jwt_valid(bearer_token)