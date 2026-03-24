import pytest
from mock import patch
from werkzeug.exceptions import BadRequest

from svc.controllers.auth_controller import exchange_auth_code


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

