import json
import uuid

import pytest
from mock import patch, ANY
from werkzeug.exceptions import Unauthorized

from svc.routes.app_routes import get_token, get_user_preferences_by_user_id, update_user_preferences_by_user_id, \
    get_user_tasks_by_user_id, delete_user_tasks_by_user_id, insert_user_task_by_user_id, update_user_task_by_user_id


@patch('svc.routes.app_routes.request')
@patch('svc.routes.app_routes.app_controller')
class TestAppRoutes:
    USER = 'user_name'
    USER_ID = '123bac34'
    PWORD = 'password'
    FAKE_JWT_TOKEN = 'fakeJwtToken'.encode('UTF-8')

    def test_token__should_respond_with_success_status_code(self, mock_controller, mock_request):
        mock_request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD})
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = get_token()

        assert actual.status_code == 200

    def test_token__should_respond_with_success_login_response(self, mock_controller, mock_request):
        mock_request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD})
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = get_token()
        json_actual = json.loads(actual.data)

        assert json_actual['bearerToken'] == self.FAKE_JWT_TOKEN.decode('UTF-8')

    def test_token__should_call_get_login(self, mock_controller, mock_request):
        mock_request.data = json.dumps({'grant_type': 'client_credentials', 'client_id': self.USER, 'client_secret': self.PWORD})
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN
        get_token()

        mock_controller.get_login.assert_called_with(self.USER, self.PWORD)

    def test_get_user_preferences_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        mock_controller.get_user_preferences.return_value = {}
        get_user_preferences_by_user_id(self.USER_ID)

        mock_controller.get_user_preferences.assert_called_with(ANY, self.USER_ID)

    def test_get_user_preferences_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.get_user_preferences.return_value = {}
        get_user_preferences_by_user_id(self.USER_ID)

        mock_controller.get_user_preferences.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_get_user_preferences_by_user_id__should_return_preference_response(self, mock_controller, mock_requests):
        expected_response = {'unit': 'metric', 'city': 'London'}
        mock_controller.get_user_preferences.return_value = expected_response

        actual = get_user_preferences_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == expected_response

    def test_get_user_preferences_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        mock_controller.get_user_preferences.return_value = {}

        actual = get_user_preferences_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_preferences_by_user_id__should_call_app_controller_with_request_data(self, mock_controller, mock_requests):
        expected_data = json.dumps({}).encode()
        mock_requests.data = expected_data
        update_user_preferences_by_user_id(self.USER_ID)

        mock_controller.save_user_preferences.assert_called_with(ANY, ANY, expected_data)

    def test_update_user_preferences_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        actual = update_user_preferences_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_preferences_by_user_id__should_return_success_content(self, mock_controller, mock_requests):
        actual = update_user_preferences_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        get_user_tasks_by_user_id(self.USER_ID, None)

        mock_controller.get_user_tasks.assert_called_with(ANY, self.USER_ID, ANY)

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        get_user_tasks_by_user_id(self.USER_ID, None)

        mock_controller.get_user_tasks.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_get_user_tasks_by_user_id__should_call_app_controller_with_task_type(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        task_type = 'hvac'
        get_user_tasks_by_user_id(self.USER_ID, task_type)

        mock_controller.get_user_tasks.assert_called_with(ANY, ANY, task_type)

    def test_get_user_tasks_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert actual.status_code == 200

    def test_get_user_tasks_by_user_id__should_return_success_content_type(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert actual.content_type == 'text/json'

    def test_get_user_tasks_by_user_id__should_return_serialize_data_from_controller(self, mock_controller, mock_requests):
        response = {'test_data': 'task'}
        mock_controller.get_user_tasks.return_value = response
        actual = get_user_tasks_by_user_id(self.USER_ID, None)

        assert json.loads(actual.data) == response

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_delete_user_tasks_by_user_id__should_call_app_controller_with_request_data(self, mock_controller, mock_requests):
        task_id = 'asjkdhflkjasd'
        delete_user_tasks_by_user_id(self.USER_ID, task_id)

        mock_controller.delete_user_task.assert_called_with(ANY, ANY, task_id)

    def test_delete_user_tasks_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        task_id = 'asjkdhflkjasd'
        actual = delete_user_tasks_by_user_id(self.USER_ID, task_id)

        assert actual.status_code == 200

    def test_delete_user_tasks_by_user_id__should_return_success_content_type(self, mock_controller, mock_requests):
        task_id = 'asjkdhflkjasd'
        actual = delete_user_tasks_by_user_id(self.USER_ID, task_id)

        assert actual.content_type == 'text/json'

    def test_insert_user_task_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.insert_user_task.return_value = {}
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_insert_user_task_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        mock_controller.insert_user_task.return_value = {}
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_insert_user_task_by_user_id__should_call_app_controller_with_request_data(self, mock_controller, mock_requests):
        data = {'test_data': 'asdfasd'}
        mock_requests.data = data
        mock_controller.insert_user_task.return_value = {}
        insert_user_task_by_user_id(self.USER_ID)

        mock_controller.insert_user_task.assert_called_with(ANY, ANY, data)

    def test_insert_user_task_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        mock_controller.insert_user_task.return_value = {}
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_insert_user_task_by_user_id__should_return_success_content_type(self, mock_controller, mock_requests):
        mock_controller.insert_user_task.return_value = {}
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_insert_user_task_by_user_id__should_return_response_data(self, mock_controller, mock_requests):
        response = {'test': 'my fake response'}
        mock_controller.insert_user_task.return_value = response
        actual = insert_user_task_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == response

    def test_update_user_task_by_user_id__should_call_app_controller_with_bearer_token(self, mock_controller, mock_requests):
        mock_requests.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.update_user_task.return_value = {}
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_task_by_user_id__should_call_app_controller_with_user_id(self, mock_controller, mock_requests):
        mock_controller.update_user_task.return_value = {}
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_task_by_user_id_should_call_app_controller_with_request_data(self, mock_controller, mock_requests):
        data = {'test_data': 'asdfasd'}
        mock_requests.data = data
        mock_controller.update_user_task.return_value = {}
        update_user_task_by_user_id(self.USER_ID)

        mock_controller.update_user_task.assert_called_with(ANY, ANY, data)

    def test_update_user_task_by_user_id__should_return_success_status_code(self, mock_controller, mock_requests):
        mock_controller.update_user_task.return_value = {}
        actual = update_user_task_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_task_by_user_id__should_return_success_content_type(self, mock_controller, mock_requests):
        mock_controller.update_user_task.return_value = {}
        actual = update_user_task_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_update_user_task_by_user_id__should_return_response_data(self, mock_controller, mock_requests):
        response = {'test': 'my fake response'}
        mock_controller.update_user_task.return_value = response
        actual = update_user_task_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == response

    def test_token__should_call_app_controller_with_old_refresh_token(self, mock_controller, mock_requests):
        old_refresh = str(uuid.uuid4())
        mock_requests.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': old_refresh})
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        get_token()

        mock_controller.refresh_bearer_token.assert_called_with(old_refresh)

    def test_token__should_return_success_status_code(self, mock_controller, mock_requests):
        mock_requests.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())})
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        assert actual.status_code == 200

    def test_token__should_return_success_content_type(self, mock_controller, mock_requests):
        mock_requests.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())})
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        assert actual.content_type == 'text/json'

    def test_token__should_return_response_data(self, mock_controller, mock_requests):
        mock_requests.data = json.dumps({'grant_type': 'refresh_token', 'refresh_token': str(uuid.uuid4())})
        mock_controller.refresh_bearer_token.return_value = self.FAKE_JWT_TOKEN
        actual = get_token()

        json_actual = json.loads(actual.data)
        assert json_actual['bearerToken'] == self.FAKE_JWT_TOKEN.decode('UTF-8')

    def test_token__should_raise_bad_request_when_wrong_grant_type(self, mock_controller, mock_requests):
        mock_requests.data = json.dumps({'grant_type': 'bearer'})
        with pytest.raises(Unauthorized):
            get_token()
