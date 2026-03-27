import json

from flask import Flask
from mock import patch, MagicMock, ANY

from svc.endpoints.auth_routes import exchange_token, provision_user
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.auth_routes.Settings')
@patch('svc.endpoints.auth_routes.auth_controller')
class TestAuthRoutes:
    FAKE_CODE = 'fake_auth_code'
    FAKE_VERIFIER = 'fake_verifier'
    FAKE_REDIRECT = 'http://localhost:3000/callback'
    ACCESS_TOKEN = 'fake_access_token'
    REFRESH_TOKEN = 'fake_refresh_token'

    def setup_method(self):
        self.app = Flask(__name__)
        self.REQUEST_BODY = json.dumps({
            'code': self.FAKE_CODE,
            'code_verifier': self.FAKE_VERIFIER,
            'redirect_uri': self.FAKE_REDIRECT
        })
        self.ctx = self.app.test_request_context(data=self.REQUEST_BODY, content_type='application/json')
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_exchange_token__should_call_controller_with_request_body(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='local')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN}
        exchange_token()

        mock_controller.exchange_auth_code.assert_called_with(json.loads(self.REQUEST_BODY))

    def test_exchange_token__should_return_success_status_code(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='local')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN}
        actual = exchange_token()

        assert actual.status_code == 200

    def test_exchange_token__should_return_empty_response_body(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='local')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN}
        actual = exchange_token()

        assert actual.data == b''

    def test_exchange_token__should_set_access_token_cookie(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='local')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN, 'expires_in': 3600}
        actual = exchange_token()

        cookie_header = actual.headers.getlist('Set-Cookie')
        access_cookie = [c for c in cookie_header if 'access_token=' in c]
        assert len(access_cookie) == 1
        assert 'HttpOnly' in access_cookie[0]

    def test_exchange_token__should_set_refresh_token_cookie(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='local')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN}
        actual = exchange_token()

        cookie_header = actual.headers.getlist('Set-Cookie')
        refresh_cookie = [c for c in cookie_header if 'refresh_token=' in c]
        assert len(refresh_cookie) == 1
        assert 'HttpOnly' in refresh_cookie[0]

    def test_exchange_token__should_set_secure_cookies_in_non_local_environment(self, mock_controller, mock_settings):
        mock_settings.get_instance.return_value = MagicMock(environment='production')
        mock_controller.exchange_auth_code.return_value = {'access_token': self.ACCESS_TOKEN, 'refresh_token': self.REFRESH_TOKEN}
        actual = exchange_token()

        cookie_header = actual.headers.getlist('Set-Cookie')
        assert all('Secure' in c for c in cookie_header)


@patch('svc.endpoints.auth_routes.auth_controller')
class TestProvisionRoutes:
    API_KEY = 'test-api-key'
    REQUEST = {'first_name': 'Jon', 'last_name': 'Test', 'email': 'jon@test.com'}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, request=self.REQUEST, headers={'X-API-Key': self.API_KEY})

    def teardown_method(self):
        self.ctx.pop()

    def test_provision_user__should_call_controller_with_api_key(self, mock_controller):
        mock_controller.provision_user.return_value = 'fake-uuid'
        provision_user()

        mock_controller.provision_user.assert_called_with(self.API_KEY, ANY)

    def test_provision_user__should_call_controller_with_request_data(self, mock_controller):
        mock_controller.provision_user.return_value = 'fake-uuid'
        provision_user()

        mock_controller.provision_user.assert_called_with(ANY, self.REQUEST)

    def test_provision_user__should_return_201_status_code(self, mock_controller):
        mock_controller.provision_user.return_value = 'fake-uuid'
        actual = provision_user()

        assert actual.status_code == 201

    def test_provision_user__should_return_json_content_type(self, mock_controller):
        mock_controller.provision_user.return_value = 'fake-uuid'
        actual = provision_user()

        assert actual.content_type == 'application/json'

    def test_provision_user__should_return_user_id_in_response(self, mock_controller):
        user_id = 'fake-uuid'
        mock_controller.provision_user.return_value = user_id
        actual = provision_user()

        assert json.loads(actual.data) == {'user_id': user_id}
