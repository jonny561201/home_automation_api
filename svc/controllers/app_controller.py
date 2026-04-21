from svc.constants.home_automation import AuthClaims
from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.tasks_repository import TasksRepository
from svc.db.repositories.user_repository import UserRepository
from svc.utilities.auth_utils import AuthClient
from svc.utilities.api_utils import send_auth0_password_reset


def reset_password(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    email = claims['email']
    send_auth0_password_reset(email)


def get_user_preferences(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        return database.get_preferences_by_user(user_id)


#TODO: get city coordinates and save in Account Repo
def save_user_preferences(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    node_id = _resolve_garage_node_id(request_data.get('garageId'))
    with UserRepository() as database:
        database.insert_preferences_by_user(user_id, request_data, node_id)


def get_user_tasks(bearer_token, task_type):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with TasksRepository() as database:
        return database.get_schedule_tasks_by_user(user_id, task_type)


def delete_user_task(bearer_token, task_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with TasksRepository() as database:
        database.delete_schedule_task_by_user(user_id, task_id)


def insert_user_task(bearer_token, task):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with TasksRepository() as database:
        return database.insert_schedule_task_by_user(user_id, task)


def update_user_task(bearer_token, task):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with TasksRepository() as database:
        return database.update_schedule_task_by_user_id(user_id, task)


def _resolve_garage_node_id(garage_id):
    if garage_id == None:
        return None
    with DeviceRepository() as database:
        device = database.get_device_info('garage_door')
        return database.get_node_id_by_device(device.id, garage_id)
