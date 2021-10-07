import json

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities import jwt_utils


def get_login(basic_token):
    user_name, pword = jwt_utils.extract_credentials(basic_token)
    with UserDatabaseManager() as user_database:
        user_info = user_database.validate_credentials(user_name, pword)
        refresh = jwt_utils.generate_refresh_token()
        user_database.insert_refresh_token(refresh)
        return jwt_utils.create_jwt_token(user_info, refresh)


<<<<<<< HEAD
def refresh_bearer_token(user_id, refresh_token):
    with UserDatabaseManager() as database:
        new_refresh = database.generate_new_refresh_token(refresh_token)
        user_info = database.get_roles_by_user(user_id)
        jwt_utils.create_jwt_token(user_info, new_refresh)
=======
def refresh_bearer_token(user_id, old_refresh):
    with UserDatabaseManager() as database:
        user_info = database.get_user_info(user_id)
        new_refresh = database.generate_new_refresh_token(old_refresh)
        return jwt_utils.create_jwt_token(user_info, new_refresh)
>>>>>>> 1a4d71a1d2c54b5ce7804110a9bef14ab488cad9


def get_user_preferences(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_preferences_by_user(user_id)


def save_user_preferences(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    user_preferences = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.insert_preferences_by_user(user_id, user_preferences)


def get_user_tasks(bearer_token, user_id, task_type):
    # jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_schedule_tasks_by_user(user_id, task_type)


def delete_user_task(bearer_token, user_id, task_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        database.delete_schedule_task_by_user(user_id, task_id)


def insert_user_task(bearer_token, user_id, task):
    jwt_utils.is_jwt_valid(bearer_token)
    request = json.loads(task.decode('UTF-8'))
    with UserDatabaseManager() as database:
        return database.insert_schedule_task_by_user(user_id, request)


def update_user_task(bearer_token, user_id, task):
    jwt_utils.is_jwt_valid(bearer_token)
    request = json.loads(task.decode('UTF-8'))
    with UserDatabaseManager() as database:
        return database.update_schedule_task_by_user_id(user_id, request)
