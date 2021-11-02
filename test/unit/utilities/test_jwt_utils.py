import uuid
from datetime import datetime, timedelta

import jwt
import pytest
import pytz
from mock import patch
from werkzeug.exceptions import Unauthorized

from svc.constants.settings_state import Settings
from svc.utilities.jwt_utils import is_jwt_valid, create_jwt_token, generate_refresh_token


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

    def test_create_jwt_token__should_return_a_valid_token(self):
        refresh = str(uuid.uuid4())
        now = datetime.now(pytz.timezone('US/Central')) + timedelta(hours=12)
        truncated_expiration = (str(now.timestamp() * 1000))[:10]
        expected_id = 12345
        expected_token_body = {'user': expected_id,
                               'refresh_token': refresh,
                               'exp': int(truncated_expiration)}

        actual = create_jwt_token(expected_id, refresh, now)

        assert jwt.decode(actual, self.JWT_SECRET, algorithms='HS256') == expected_token_body

    @patch('svc.utilities.jwt_utils.uuid')
    def test_generate_refresh_token__should_return_generated_id(self, mock_uuid):
        refresh = uuid.uuid4()
        mock_uuid.uuid4.return_value = refresh
        actual = generate_refresh_token()

        assert actual == str(refresh)

    def test_is_jwt_valid__should_raise_exception_if_secret_is_not_set(self):
        self.SETTINGS.settings = {'DevJwtSecret': ''}
        jwt_body = {'fakeBody': 'valueValue'}
        jwt_secret = 'testSecret'
        jwt_token = jwt.encode(jwt_body, jwt_secret, algorithm='HS256').decode('UTF-8')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)
