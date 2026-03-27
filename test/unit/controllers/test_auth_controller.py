import pytest
from mock import patch
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.controllers.auth_controller import exchange_auth_code, provision_user


@patch('svc.controllers.auth_controller.api_utils')
class TestAuthController:
    FAKE_CODE = 'fake_auth_code'
    FAKE_VERIFIER = 'fake_verifier'
    FAKE_REDIRECT = 'http://localhost:3000/callback'

    def test_exchange_auth_code__should_call_api_utils(self, mock_api):
        request_data = {'code': self.FAKE_CODE, 'code_verifier': self.FAKE_VERIFIER, 'redirect_uri': self.FAKE_REDIRECT}
        exchange_auth_code(request_data)

        mock_api.exchange_auth0_code.assert_called_with(self.FAKE_CODE, self.FAKE_VERIFIER, self.FAKE_REDIRECT)

    def test_exchange_auth_code__should_return_response_from_api_utils(self, mock_api):
        expected = {'access_token': 'abc', 'refresh_token': 'xyz'}
        mock_api.exchange_auth0_code.return_value = expected
        request_data = {'code': self.FAKE_CODE, 'code_verifier': self.FAKE_VERIFIER, 'redirect_uri': self.FAKE_REDIRECT}
        actual = exchange_auth_code(request_data)

        assert actual == expected

    def test_exchange_auth_code__should_raise_bad_request_when_code_missing(self, mock_api):
        request_data = {'code_verifier': self.FAKE_VERIFIER, 'redirect_uri': self.FAKE_REDIRECT}
        with pytest.raises(BadRequest):
            exchange_auth_code(request_data)

    def test_exchange_auth_code__should_raise_bad_request_when_code_verifier_missing(self, mock_api):
        request_data = {'code': self.FAKE_CODE, 'redirect_uri': self.FAKE_REDIRECT}
        with pytest.raises(BadRequest):
            exchange_auth_code(request_data)

    def test_exchange_auth_code__should_raise_bad_request_when_redirect_uri_missing(self, mock_api):
        request_data = {'code': self.FAKE_CODE, 'code_verifier': self.FAKE_VERIFIER}
        with pytest.raises(BadRequest):
            exchange_auth_code(request_data)


@patch('svc.controllers.auth_controller.AccountRepository')
@patch('svc.controllers.auth_controller.Settings')
class TestProvisionUser:
    API_KEY = 'test-api-key'
    REQUEST = {'first_name': 'Jon', 'last_name': 'Test', 'email': 'jon@test.com'}

    def test_provision_user__should_raise_unauthorized_when_api_key_is_none(self, mock_settings, mock_db):
        with pytest.raises(Unauthorized):
            provision_user(None, self.REQUEST)

    def test_provision_user__should_raise_unauthorized_when_api_key_does_not_match(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        with pytest.raises(Unauthorized):
            provision_user('wrong-key', self.REQUEST)

    def test_provision_user__should_raise_bad_request_when_first_name_missing(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        with pytest.raises(BadRequest):
            provision_user(self.API_KEY, {'last_name': 'Test', 'email': 'test@test.com'})

    def test_provision_user__should_raise_bad_request_when_last_name_missing(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        with pytest.raises(BadRequest):
            provision_user(self.API_KEY, {'first_name': 'Jon', 'email': 'test@test.com'})

    def test_provision_user__should_raise_bad_request_when_email_missing(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        with pytest.raises(BadRequest):
            provision_user(self.API_KEY, {'first_name': 'Jon', 'last_name': 'Test'})

    def test_provision_user__should_call_database_with_user_data(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        provision_user(self.API_KEY, self.REQUEST)

        mock_db.return_value.__enter__.return_value.provision_user.assert_called_with('Jon', 'Test', 'jon@test.com')

    def test_provision_user__should_return_user_id_from_database(self, mock_settings, mock_db):
        mock_settings.get_instance.return_value.Authority.provision_api_key = self.API_KEY
        user_id = 'fake-uuid'
        mock_db.return_value.__enter__.return_value.provision_user.return_value = user_id
        actual = provision_user(self.API_KEY, self.REQUEST)

        assert actual == user_id
