import json
import uuid
from datetime import timedelta, datetime

import jwt
import pytz
from mock import patch, ANY

from svc.controllers.app_controller import get_login, get_user_preferences, save_user_preferences, get_user_tasks, \
    delete_user_task, insert_user_task, update_user_task, refresh_bearer_token


@patch('svc.controllers.app_controller.UserDatabaseManager')
@patch('svc.controllers.app_controller.jwt_utils')
class TestLoginController:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256').decode('UTF-8')
    USER = 'user_name'
    PWORD = 'password'
    USER_ID = str(uuid.uuid4())

    def test_get_login__should_call_validate_credentials_with_post_body(self, mock_jwt, mock_db):
        get_login(self.USER, self.PWORD)

        mock_db.return_value.__enter__.return_value.validate_credentials.assert_called_with(self.USER, self.PWORD)

    @patch('svc.controllers.app_controller.datetime')
    def test_get_login__should_call_create_jwt_token_with_database_response(self, mock_date, mock_jwt, mock_db):
        user_info = {'user_id': 'sdfasdf', 'role_name': 'lighting'}
        now = datetime.now()
        mock_date.now.return_value = now
        refresh = str(uuid.uuid4())
        mock_jwt.generate_refresh_token.return_value = refresh
        mock_db.return_value.__enter__.return_value.validate_credentials.return_value = user_info
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.USER, self.PWORD)
        expected_date = now + timedelta(hours=12)

        mock_jwt.create_jwt_token.assert_called_with(user_info, refresh, expected_date)

    def test_get_login__should_return_response_from_jwt_service(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        mock_jwt.create_jwt_token.return_value = self.BEARER_TOKEN
        actual = get_login(self.USER, self.PWORD)

        assert actual == self.BEARER_TOKEN

    @patch('svc.controllers.app_controller.datetime')
    def test_get_login__should_create_expiration_date(self, mock_date, mock_jwt, mock_db):
        get_login(self.USER, self.PWORD)

        mock_date.now.assert_called_with(tz=pytz.timezone('US/Central'))

    @patch('svc.controllers.app_controller.datetime')
    def test_get_login__should_store_refresh_token_in_db(self, mock_date, mock_jwt, mock_db):
        now = datetime.now()
        mock_date.now.return_value = now
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        mock_db.return_value.__enter__.return_value.validate_credentials.return_value = {'user_id': self.USER_ID}
        refresh = str(uuid.uuid4())
        mock_jwt.generate_refresh_token.return_value = refresh
        expected_date = now + timedelta(hours=12)

        get_login(self.USER, self.PWORD)

        mock_db.return_value.__enter__.return_value.insert_refresh_token.assert_called_with(self.USER_ID, refresh, expected_date)

    def test_refresh_bearer_token__should_make_call_to_db_to_generate_new_refresh_token(self, mock_jwt, mock_db):
        old_refresh = str(uuid.uuid4())
        refresh_bearer_token(old_refresh)

        mock_db.return_value.__enter__.return_value.generate_new_refresh_token.assert_called_with(old_refresh)

    def test_refresh_bearer_token__should_make_call_to_get_user_info_from_db(self, mock_jwt, mock_db):
        old_refresh = str(uuid.uuid4())
        refresh_data = {'user_id': self.USER_ID, 'refresh_token': str(uuid.uuid4())}
        mock_db.return_value.__enter__.return_value.generate_new_refresh_token.return_value = refresh_data
        refresh_bearer_token(old_refresh)

        mock_db.return_value.__enter__.return_value.get_user_info.assert_called_with(self.USER_ID)

    def test_refresh_bearer_token__should_have_jwt_util_create_new_bearer_token(self, mock_jwt, mock_db):
        old_refresh = str(uuid.uuid4())
        new_refresh = str(uuid.uuid4())
        user_info = {'first_name': 'Paul', 'last_name': 'Atreides'}
        refresh_data = {'user_id': self.USER_ID, 'refresh_token': new_refresh}
        mock_db.return_value.__enter__.return_value.generate_new_refresh_token.return_value = refresh_data
        mock_db.return_value.__enter__.return_value.get_user_info.return_value = user_info
        refresh_bearer_token(old_refresh)

        mock_jwt.create_jwt_token.assert_called_with(user_info, new_refresh)

    def test_refresh_bearer_token__should_return_the_new_bearer_token(self, mock_jwt, mock_db):
        old_refresh = str(uuid.uuid4())
        mock_jwt.create_jwt_token.return_value = self.BEARER_TOKEN
        actual = refresh_bearer_token(old_refresh)

        assert actual == self.BEARER_TOKEN

    def test_get_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_user_preferences(self.BEARER_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_preferences__should_call_get_preferences_by_user(self, mock_jwt, mock_db):
        get_user_preferences(self.BEARER_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_preferences__should_return_preferences_response(self, mock_jwt, mock_db):
        prefs = {'unit': 'imperial', 'city': 'Des Moines'}
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = prefs

        actual = get_user_preferences(self.BEARER_TOKEN, self.USER_ID)

        assert actual == prefs

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

    # TODO: find a way to have the two services authorize and pass tokens
    # def test_get_user_tasks__should_validate_bearer_token(self, mock_jwt, mock_db):
    #     get_user_tasks(self.BEARER_TOKEN, self.USER_ID)
    #     mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_tasks__should_call_get_schedule_tasks_by_user(self, mock_jwt, mock_db):
        get_user_tasks(self.BEARER_TOKEN, self.USER_ID, 'hvac')
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID, ANY)

    def test_get_user_tasks__should_call_get_schedule_tasks_by_task_type(self, mock_jwt, mock_db):
        task_type = 'sunrise alarm'
        get_user_tasks(self.BEARER_TOKEN, self.USER_ID, task_type)
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(ANY, task_type)

    def test_get_user_tasks__should_return_user_tasks_from_database(self, mock_jwt, mock_db):
        response = [{'task_id': '12312bas-12312basdd-12312bjsd-123b123v'}]
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = response
        actual = get_user_tasks(self.BEARER_TOKEN, self.USER_ID, 'turn on')

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
        task = {'test': 'data'}
        request_data = json.dumps(task).encode('UTF-8')
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_user_id(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(self.USER_ID, ANY)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_task(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        insert_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(ANY, task)

    def test_insert_user_task__should_return_database_response(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        response = {'task_id': '123basdf-123basd-345jasdf-asd558'}
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.return_value = response
        actual = insert_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)

        assert actual == response

    def test_update_user_task__should_validate_bearer_token(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        update_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_update_user_task__should_call_update_schedule_task_by_user_id_with_user_id(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        update_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.assert_called_with(self.USER_ID, ANY)

    def test_update_user_task__should_call_update_schedule_task_by_user_id_with_new_task(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        update_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.assert_called_with(self.USER_ID, task)

    def test_update_user_task__should_return_response_from_db_layer(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        request_data = json.dumps(task).encode('UTF-8')
        response = {'fakeItem': 'item'}
        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.return_value = response
        actual = update_user_task(self.BEARER_TOKEN, self.USER_ID, request_data)

        assert actual == response
