import base64
import json

from mock import patch, ANY

from svc.routes.app_routes import app_login, get_user_preferences_by_user_id, update_user_preferences_by_user_id, \
    update_user_password, get_roles_by_user_id


@patch('svc.routes.app_routes.request')
@patch('svc.routes.app_routes.app_controller')
class TestAppRoutes:
    USER = 'user_name'
    USER_ID = '123bac34'
    PWORD = 'password'
    FAKE_JWT_TOKEN = 'fakeJwtToken'.encode('UTF-8')
    CREDS = ('%s:%s' % (USER, PWORD)).encode()
    ENCODED_CREDS = base64.b64encode(CREDS).decode('UTF-8')
    AUTH_HEADER = {"Authorization": "Basic " + ENCODED_CREDS}

    def test_app_login__should_respond_with_success_status_code(self, mock_controller, mock_request):
        mock_request.headers = self.AUTH_HEADER
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = app_login()

        assert actual.status_code == 200

    def test_app_login__should_respond_with_success_login_response(self, mock_controller, mock_request):
        mock_request.headers = self.AUTH_HEADER
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN

        actual = app_login()
        json_actual = json.loads(actual.data)

        assert json_actual['bearerToken'] == self.FAKE_JWT_TOKEN.decode('UTF-8')

    def test_app_login__should_call_get_login(self, mock_controller, mock_request):
        mock_request.headers = self.AUTH_HEADER
        mock_controller.get_login.return_value = self.FAKE_JWT_TOKEN
        app_login()

        expected_bearer = "Basic " + self.ENCODED_CREDS
        mock_controller.get_login.assert_called_with(expected_bearer)

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

    def test_update_user_password__should_call_change_password_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_password__should_call_change_password_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_password__should_call_change_password_controller_with_data(self, mock_controller, mock_request):
        request_data = {'fakeData': 'doesnt matter'}
        mock_request.data = request_data
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(ANY, ANY, request_data)

    def test_update_user_password__should_return_success_status_code(self, mock_controller, mock_request):
        actual = update_user_password(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_password__should_return_success_content(self, mock_controller, mock_request):
        actual = update_user_password(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_get_roles_by_user_id__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_get_roles_by_user_id__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(ANY, self.USER_ID)

    def test_get_roles_by_user_id__should_not_throw_exception_when_no_header(self, mock_controller, mock_request):
        mock_request.headers = {}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(None, ANY)

    def test_get_roles_by_user_id__should_return_success_status_code(self, mock_controller, mock_request):
        mock_request.headers = {}
        actual = get_roles_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_get_roles_by_user_id__should_return_success_headers(self, mock_controller, mock_request):
        mock_request.headers = {}
        actual = get_roles_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'
