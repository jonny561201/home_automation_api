import base64
from datetime import datetime, timedelta

import jwt
import pytest
import pytz
from mock import patch
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.constants.settings_state import Settings
from svc.utilities.jwt_utils import is_jwt_valid, create_jwt_token, extract_credentials


class TestJwt:
    JWT_BODY = None
    JWT_SECRET = 'testSecret'

    def setup_method(self):
        self.JWT_BODY = {'fakeBody': 'valueValue'}
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DevJwtSecret': self.JWT_SECRET}

    def test_is_jwt_valid__should_not_fail_if_it_can_be_decrypted(self):
        jwt_token = jwt.encode(self.JWT_BODY, self.JWT_SECRET, algorithm='HS256').decode('UTF-8')

        is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_it_cannot_be_decrypted(self):
        jwt_token = jwt.encode(self.JWT_BODY, 'badSecret', algorithm='HS256').decode('UTF-8')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_has_expired(self):
        expired_date = datetime.now() - timedelta(hours=1)
        self.JWT_BODY['exp'] = expired_date
        jwt_token = jwt.encode(self.JWT_BODY, self.JWT_SECRET, algorithm='HS256').decode('UTF-8')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_is_none(self):
        jwt_token = None

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_is_invalid_string(self):
        self.SETTINGS.dev_mode = False
        jwt_token = 'abc123'

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_succeed_when_provided_bearer_text_in_token(self):
        jwt_body = {'fakeBody': 'valueValue'}
        jwt_token = 'Bearer ' + jwt.encode(jwt_body, self.JWT_SECRET, algorithm='HS256').decode('UTF-8')

        is_jwt_valid(jwt_token)

    @patch('svc.utilities.jwt_utils.datetime')
    def test_create_jwt_token__should_return_a_valid_token(self, mock_date):
        now = datetime.now(pytz.timezone('US/Central'))
        mock_date.now.return_value = now
        expected_expiration = now + timedelta(hours=2)
        truncated_expiration = (str(expected_expiration.timestamp() * 1000))[:10]
        expected_id = 12345
        expected_token_body = {'user': expected_id, 'exp': int(truncated_expiration)}

        actual = create_jwt_token(expected_id)

        assert jwt.decode(actual, self.JWT_SECRET, algorithms='HS256') == expected_token_body

    def test_extract_credentials__should_return_valid_credentials(self):
        user = "user"
        pword = "password"
        creds = "%s:%s" % (user, pword)
        encoded_token = base64.b64encode(creds.encode())
        bearer_token = "Basic %s" % encoded_token.decode('UTF-8')

        actual_user, actual_pass = extract_credentials(bearer_token)

        assert actual_pass == pword
        assert actual_user == user

    def test_extract_credentials__should_return_valid_credentials_when_missing_basic(self):
        user = "user"
        pword = "password"
        creds = "%s:%s" % (user, pword)
        encoded_token = base64.b64encode(creds.encode())
        bearer_token = encoded_token.decode('UTF-8')

        actual_user, actual_pass = extract_credentials(bearer_token)

        assert actual_pass == pword
        assert actual_user == user

    def test_extract_credentials__should_throw_bad_request_when_no_token(self):
        with pytest.raises(BadRequest):
            extract_credentials(None)

    def test_extract_credentials__should(self):
        with pytest.raises(BadRequest):
            extract_credentials("")

    def test_is_jwt_valid__should_raise_exception_if_secret_is_not_set(self):
        self.SETTINGS.settings = {'DevJwtSecret': ''}
        jwt_body = {'fakeBody': 'valueValue'}
        jwt_secret = 'testSecret'
        jwt_token = jwt.encode(jwt_body, jwt_secret, algorithm='HS256').decode('UTF-8')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)
