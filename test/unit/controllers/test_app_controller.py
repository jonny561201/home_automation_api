import uuid

import jwt
from mock import patch, ANY

from svc.constants.home_automation import AuthClaims
from svc.controllers.app_controller import get_user_preferences, save_user_preferences, get_user_tasks, \
    delete_user_task, insert_user_task, update_user_task, reset_password


@patch('svc.controllers.app_controller.UserRepository')
@patch('svc.controllers.app_controller.AuthClient')
class TestAppControllerAccount:
    USER_ID = str(uuid.uuid4())
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = jwt.encode(CLAIMS, 'fake_jwt_secret', algorithm='HS256')
    USER = 'user_name'

    def test_reset_password__should_validate_bearer_token(self, mock_jwt, mock_db):
        reset_password(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_user_preferences(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_preferences__should_call_get_preferences_by_user(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_user_preferences(self.BEARER_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_preferences__should_return_preferences_response(self, mock_jwt, mock_db):
        prefs = {'unit': 'imperial', 'city': 'Des Moines'}
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = prefs

        actual = get_user_preferences(self.BEARER_TOKEN)

        assert actual == prefs

    def test_save_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        save_user_preferences(bearer_token, {})

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(bearer_token)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        bearer_token = 'fakeBearerToken'
        save_user_preferences(bearer_token, {})

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(self.USER_ID, ANY)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_info(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        user_preferences = {'city': 'Berlin'}

        save_user_preferences(bearer_token, user_preferences)

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(ANY, user_preferences)


@patch('svc.controllers.app_controller.send_auth0_password_reset')
@patch('svc.controllers.app_controller.AuthClient')
class TestResetAccount:
    USER_ID = str(uuid.uuid4())
    EMAIL = 'test@test.com'
    CLAIMS = {AuthClaims.USER_ID: USER_ID, 'email': EMAIL}
    BEARER_TOKEN = jwt.encode(CLAIMS, 'fake_jwt_secret', algorithm='HS256')

    def test_reset_password__should_validate_bearer_token(self, mock_jwt, mock_auth):
        reset_password(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_reset_password__should_call_auth0_service_with_email(self, mock_jwt, mock_auth):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        reset_password(self.BEARER_TOKEN)

        mock_auth.assert_called_with(self.EMAIL)


@patch('svc.controllers.app_controller.TasksRepository')
@patch('svc.controllers.app_controller.AuthClient')
class TestAppControllerTasks:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER_ID = str(uuid.uuid4())

    # TODO: find a way to have the two services authorize and pass tokens
    # def test_get_user_tasks__should_validate_bearer_token(self, mock_jwt, mock_db):
    #     get_user_tasks(self.BEARER_TOKEN, self.USER_ID)
    #     mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_tasks__should_call_get_schedule_tasks_by_user(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        get_user_tasks(self.BEARER_TOKEN, 'hvac')
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID, ANY)

    def test_get_user_tasks__should_call_get_schedule_tasks_by_task_type(self, mock_jwt, mock_db):
        task_type = 'sunrise alarm'
        get_user_tasks(self.BEARER_TOKEN, task_type)
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(ANY, task_type)

    def test_get_user_tasks__should_return_user_tasks_from_database(self, mock_jwt, mock_db):
        response = [{'task_id': '12312bas-12312basdd-12312bjsd-123b123v'}]
        mock_db.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = response
        actual = get_user_tasks(self.BEARER_TOKEN, 'turn on')

        assert actual == response

    def test_delete_user_task__should_validate_bearer_token(self, mock_jwt, mmock_db):
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, task_id)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_delete_user_task__should_call_get_schedule_tasks_by_user_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, task_id)
        mock_db.return_value.__enter__.return_value.delete_schedule_task_by_user.assert_called_with(self.USER_ID, ANY)

    def test_delete_user_task__should_call_get_schedule_tasks_by_user_with_task_id(self, mock_jwt, mock_db):
        task_id = 'jklasdf89734'
        delete_user_task(self.BEARER_TOKEN, task_id)
        mock_db.return_value.__enter__.return_value.delete_schedule_task_by_user.assert_called_with(ANY, task_id)

    def test_insert_user_task__should_validate_bearer_token(self, mock_jwt, mock_db):
        task = {'test': 'data'}
        insert_user_task(self.BEARER_TOKEN, task)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        task = {'alarm_time': '00:01:00'}
        insert_user_task(self.BEARER_TOKEN, task)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(self.USER_ID, ANY)

    def test_insert_user_task__should_call_insert_schedule_task_by_user_with_task(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        insert_user_task(self.BEARER_TOKEN, task)
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.assert_called_with(ANY, task)

    def test_insert_user_task__should_return_database_response(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        response = {'task_id': '123basdf-123basd-345jasdf-asd558'}
        mock_db.return_value.__enter__.return_value.insert_schedule_task_by_user.return_value = response
        actual = insert_user_task(self.BEARER_TOKEN, task)

        assert actual == response

    def test_update_user_task__should_validate_bearer_token(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        update_user_task(self.BEARER_TOKEN, task)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_update_user_task__should_call_update_schedule_task_by_user_id_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        task = {'alarm_time': '00:01:00'}
        update_user_task(self.BEARER_TOKEN, task)

        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.assert_called_with(self.USER_ID, ANY)

    def test_update_user_task__should_call_update_schedule_task_by_user_id_with_new_task(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        task = {'alarm_time': '00:01:00'}
        update_user_task(self.BEARER_TOKEN, task)

        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.assert_called_with(self.USER_ID, task)

    def test_update_user_task__should_return_response_from_db_layer(self, mock_jwt, mock_db):
        task = {'alarm_time': '00:01:00'}
        response = {'fakeItem': 'item'}
        mock_db.return_value.__enter__.return_value.update_schedule_task_by_user_id.return_value = response
        actual = update_user_task(self.BEARER_TOKEN, task)

        assert actual == response