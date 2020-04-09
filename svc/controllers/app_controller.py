import json

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities import jwt_utils


def get_login(basic_token):
    user_name, pword = jwt_utils.extract_credentials(basic_token)
    with UserDatabaseManager() as user_database:
        user_info = user_database.validate_credentials(user_name, pword)
        return jwt_utils.create_jwt_token(user_info)


def get_user_preferences(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_preferences_by_user(user_id)


def save_user_preferences(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    user_preferences = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.insert_preferences_by_user(user_id, user_preferences)


def change_password(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    request = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.change_user_password(user_id, request['oldPassword'], request['newPassword'])
