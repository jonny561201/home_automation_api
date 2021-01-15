import json
import datetime

import jwt
from mock import patch, ANY

from svc.controllers.app_controller import get_login, get_user_preferences, save_user_preferences, get_user_tasks, \
    delete_user_task, insert_user_task


@patch('svc.controllers.app_controller.UserDatabaseManager')
@patch('svc.controllers.app_controller.jwt_utils')
class TestLoginController:
    BASIC_AUTH_TOKEN = 'not_a_real_auth_token'
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256').decode('UTF-8')
    USER = 'user_name'
    PWORD = 'password'
    USER_ID = 'fake_user_id'

    def test_get_login__should_call_validate_credentials_with_post_body(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_db.return_value.__enter__.return_value.validate_credentials.assert_called_with(self.USER, self.PWORD)

    def test_get_login__should_call_extract_credentials(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_jwt.extract_credentials.assert_called_with(self.BASIC_AUTH_TOKEN)

    def test_get_login__should_call_create_jwt_token_with_database_response(self, mock_jwt, mock_db):
        user_info = {'user_id': 'sdfasdf', 'role_name': 'lighting'}
        mock_db.return_value.__enter__.return_value.validate_credentials.return_value = user_info
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_jwt.create_jwt_token.assert_called_with(user_info)

    def test_get_login__should_return_response_from_jwt_service(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        mock_jwt.create_jwt_token.return_value = self.BEARER_TOKEN
        actual = get_login(self.BASIC_AUTH_TOKEN)

        assert actual == self.BEARER_TOKEN

    def test_get_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BASIC_AUTH_TOKEN)

    def test_get_user_preferences__should_call_get_preferences_by_user(self, mock_jwt, mock_db):
        get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_preferences__should_return_preferences_response(self, mock_jwt, mock_db):
        alarm_time = datetime.datetime.now().time()
        prefs = {'unit': 'imperial', 'city': 'Des Moines', 'light_alarm': {'alarm_time': alarm_time}}
        expected_prefs = {'unit': 'imperial', 'city': 'Des Moines', 'light_alarm': {'alarm_time': str(alarm_time)}}
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = prefs

        actual = get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        assert actual == expected_prefs

    def test_save_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        request_data = json.dumps({}).encode()

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_jwt.is_jwt_valid.assert_called_with(bearer_token)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_id(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        request_data = json.dumps({}).encode()

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(self.USER_ID, ANY)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_info(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        user_preferences = {'city': 'Berlin'}
        request_data = json.dumps(user_preferences).encode('UTF-8')

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(ANY, user_preferences)

    def test_get_user_tasks__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_user_tasks(self.BEARER_TOKEN, self.USER_ID)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_tasks__should_call_get_schedule_tasks_by_user(self, mock_jwt, mock_db):
        get_user_tasks(self.BEARER_TOKEN, self.USER_ID)
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID)

    def test_get_user_tasks__should_return_user_tasks_from_database(self, mock_jwt, mock_db):
        response = [{'task_id': '12312bas-12312basdd-12312bjsd-123b123v'}]
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = response
        actual = get_user_tasks(self.BEARER_TOKEN, self.USER_ID)

        assert actual == response

    def test_delete_user_task__should_validate_bearer_token(self, mock_jwt, mock_db):
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, self.USER_ID, task_id)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_delete_user_task__should_call_get_schedule_tasks_by_user_with_user_id(self, mock_jwt, mock_db):
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, self.USER_ID, task_id)
        mock_db.return_value.__enter__.return_value.delete_schedule_task_by_user.assert_called_with(self.USER_ID, ANY)

    def test_delete_user_task__should_call_get_schedule_tasks_by_user_with_task_id(self, mock_jwt, mock_db):
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, self.USER_ID, task_id)
        mock_db.return_value.__enter__.return_value.delete_schedule_task_by_user.assert_called_with(ANY, task_id)

    def test_insert_user_task__should_validate_bearer_token(self, mock_jwt, mock_db):
        task = {}
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, task)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_user_id(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, task)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(self.USER_ID, ANY)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_task(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, task)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(ANY, task)
