import json
import uuid

import pytest
from flask import Flask, request
from mock import patch, ANY
from werkzeug.exceptions import Unauthorized

from svc.endpoints.app_routes import get_token, get_user_preferences_by_user_id, update_user_preferences_by_user_id, \
    get_user_tasks_by_user_id, delete_user_tasks_by_user_id, insert_user_task_by_user_id, update_user_task_by_user_id
from svc.models.app import Preference, Tasks, Task


@patch('svc.endpoints.app_routes.app_controller')
class TestAppRoutes:
    USER = 'user_name'
    USER_ID = '123bac34'
    PWORD = 'password'
    FAKE_JWT_TOKEN = 'fakeJwtToken'

    def setup_method(self):
        self.app = Flask(__name__)
        self.TASK = Task(taskId='1', taskType='x', enabled=True, hvacMode='auto', alarmDays='M', hvacStopTemp=68, hvacStartTemp=72, alarmGroupName='Test', alarmLightGroup='1')
        self.PREFERENCES = Preference(isImperial=False, isFahrenheit=False, city='York', tempUnit='Celsius', measureUnit='cm', garageId=1, garageDoor='Kals')
        self.TASKS = Tasks(tasks=[])
        self.ctx = self.app.test_request_context(headers={'Authorization': self.FAKE_JWT_TOKEN})
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_token__should_respond_with_success_status_code(self, mock_controller):
        request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD}).encode()
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = get_token()

        assert actual.status_code == 200

    def test_token__should_respond_with_success_login_response(self, mock_controller):
        request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD}).encode()
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = get_token()
        json_actual = json.loads(actual.data)

        assert json_actual['bearerToken'] == self.FAKE_JWT_TOKEN

    def test_token__should_call_get_login(self, mock_controller):
        request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD}).encode()
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN
        get_token()

        mock_controller.get_login.assert_called_with(self.USER, self.PWORD)

    def test_get_user_preferences_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        mock_controller.get_user_preferences.return_value = self.PREFERENCES
        get_user_preferences_by_user_id(self.USER_ID)

        mock_controller.get_user_preferences.assert_called_with(ANY, self.USER_ID)

    def test_get_user_preferences_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_user_preferences.return_value = self.PREFERENCES
        get_user_preferences_by_user_id(self.USER_ID)

        mock_controller.get_user_preferences.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_get_user_preferences_by_user_id__should_return_preference_response(self, mock_controller):
        mock_controller.get_user_preferences.return_value = self.PREFERENCES

        actual = get_user_preferences_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == self.PREFERENCES.to_dict()

    def test_get_user_preferences_by_user_id__should_return_success_status_code(self, mock_controller):
        mock_controller.get_user_preferences.return_value = self.PREFERENCES

        actual = get_user_preferences_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_request_data(self, mock_controller):
        expected_data = json.dumps({}).encode()
        request.data = expected_data
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(ANY, ANY, expected_data)

    def test_update_user_preferences_by_user_id__should_return_success_status_code(self, mock_controller):
        actual = update_user_preferences_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_preferences_by_user_id__should_return_success_content(self, mock_controller):
        actual = update_user_preferences_by_user_id(self.USER_ID)

        assert actual.content_type == 'application/json'

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        get_user_tasks_by_user_id(self.USER_ID, None)

        mock_controller.get_user_tasks.assert_called_with(ANY, self.USER_ID, ANY)

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        get_user_tasks_by_user_id(self.USER_ID, None)

        mock_controller.get_user_tasks.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_task_type(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        task_type = 'hvac'
        get_user_tasks_by_user_id(self.USER_ID, task_type)

        mock_controller.get_user_tasks.assert_called_with(ANY, ANY, task_type)

    def test_get_user_tasks_by_user_id__should_return_success_status_code(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert actual.status_code == 200

    def test_get_user_tasks_by_user_id__should_return_success_content_type(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert actual.content_type == 'application/json'

    def test_get_user_tasks_by_user_id__should_return_serialize_data_from_controller(self, mock_controller):
        mock_controller.get_user_tasks.return_value = self.TASKS
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert json.loads(actual.data) == self.TASKS.to_dict()

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_request_data(self, mock_controller):
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(ANY, ANY, task_id)

    def test_delete_user_tasks_by_user_id__should_return_success_status_code(self, mock_controller):
        task_id = 'asjkdhflkjasd'
        actual = delete_user_tasks_by_user_id(self.USER_ID, task_id)

        assert actual.status_code == 200

    def test_delete_user_tasks_by_user_id__should_return_success_content_type(self, mock_controller):
        task_id = 'asjkdhflkjasd'
        actual = delete_user_tasks_by_user_id(self.USER_ID, task_id)

        assert actual.content_type == 'application/json'

    def test_insert_user_task_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        mock_controller.insert_user_task.return_value = self.TASKS
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_insert_user_task_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        mock_controller.insert_user_task.return_value = self.TASKS
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_insert_user_task_by_user_id__should_call_app_controller_with_request_data(self, mock_controller):
        data = json.dumps({'test_data': 'asdfasd'}).encode()
        request.data = data
        mock_controller.insert_user_task.return_value = self.TASKS
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(ANY, ANY, data)

    def test_insert_user_task_by_user_id__should_return_success_status_code(self, mock_controller):
        mock_controller.insert_user_task.return_value = self.TASKS
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_insert_user_task_by_user_id__should_return_success_content_type(self, mock_controller):
        mock_controller.insert_user_task.return_value = self.TASKS
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert actual.content_type == 'application/json'

    def test_insert_user_task_by_user_id__should_return_response_data(self, mock_controller):
        mock_controller.insert_user_task.return_value = self.TASKS
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == self.TASKS.to_dict()

    def test_update_user_task_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller):
        mock_controller.update_user_task.return_value = self.TASK
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_task_by_user_id__should_call_app_controller_with_user_id(self, mock_controller):
        mock_controller.update_user_task.return_value = self.TASK
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_task_by_user_id_should_call_app_controller_with_request_data(self, mock_controller):
        data = json.dumps({'test_data': 'asdfasd'}).encode()
        request.data = data
        mock_controller.update_user_task.return_value = self.TASK
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(ANY, ANY, data)

    def test_update_user_task_by_user_id__should_return_success_status_code(self, mock_controller):
        mock_controller.update_user_task.return_value = self.TASK
        actual = update_user_task_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_task_by_user_id__should_return_success_content_type(self, mock_controller):
        mock_controller.update_user_task.return_value = self.TASK
        actual = update_user_task_by_user_id(self.USER_ID)

        assert actual.content_type == 'application/json'

    def test_update_user_task_by_user_id__should_return_response_data(self, mock_controller):
        mock_controller.update_user_task.return_value = self.TASK
        actual = update_user_task_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == self.TASK.to_dict()

    def test_token__should_call_app_controller_with_old_refresh_token(self, mock_controller):
        old_refresh = str(uuid.uuid4())
        request.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': old_refresh}).encode()
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        get_token()

        mock_controller.refresh_bearer_token.assert_called_with(old_refresh)

    def test_token__should_return_success_status_code(self, mock_controller):
        request.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())}).encode()
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        assert actual.status_code == 200

    def test_token__should_return_success_content_type(self, mock_controller):
        request.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())}).encode()
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        assert actual.content_type == 'application/json'

    def test_token__should_return_response_data(self, mock_controller):
        request.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())}).encode()
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        json_actual = json.loads(actual.data)
        assert json_actual['bearerToken'] == self.FAKE_JWT_TOKEN

    def test_token__should_raise_bad_request_when_wrong_grant_type(self, mock_controller):
        request.data = json.dumps({'grant_type': 'bearer'}).encode()
        with pytest.raises(Unauthorized):
            get_token()
