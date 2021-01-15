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
        prefs = database.get_preferences_by_user(user_id)
        prefs.get('light_alarm')['alarm_time'] = str(prefs.get('light_alarm')['alarm_time'])
        return prefs


def save_user_preferences(bearer_token, user_id, request_data):
    jwt_utils.is_jwt_valid(bearer_token)
    user_preferences = json.loads(request_data.decode('UTF-8'))
    with UserDatabaseManager() as database:
        database.insert_preferences_by_user(user_id, user_preferences)


def get_user_tasks(bearer_token, user_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.get_schedule_tasks_by_user(user_id)


def delete_user_task(bearer_token, user_id, task_id):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        database.delete_schedule_task_by_user(user_id, task_id)


def insert_user_task(bearer_token, user_id, task):
    jwt_utils.is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        return database.insert_schedule_task_by_user(user_id, json.loads(task.decode('UTF-8')))
