import uuid
from datetime import datetime, timedelta

import jwt
import pytest
from mock import patch
from zoneinfo import ZoneInfo
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from werkzeug.exceptions import Unauthorized, Forbidden

from svc.config.settings_state import Settings
from svc.utilities.jwt_utils import is_jwt_valid, create_jwt_token, generate_refresh_token, AuthClient


class TestJwt:
    JWT_BODY = None
    JWT_SECRET = 'testSecret'

    def setup_method(self):
        self.JWT_BODY = {'fakeBody': 'valueValue'}
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS._settings = {'JwtSecret': self.JWT_SECRET}

    def test_is_jwt_valid__should_not_fail_if_it_can_be_decrypted(self):
        jwt_token = jwt.encode(self.JWT_BODY, self.JWT_SECRET, algorithm='HS256')

        is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_it_cannot_be_decrypted(self):
        jwt_token = jwt.encode(self.JWT_BODY, 'badSecret', algorithm='HS256')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_has_expired(self):
        expired_date = datetime.now() - timedelta(hours=1)
        self.JWT_BODY['exp'] = expired_date
        jwt_token = jwt.encode(self.JWT_BODY, self.JWT_SECRET, algorithm='HS256')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_is_none(self):
        jwt_token = None

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_raise_unauthorized_if_token_is_invalid_string(self):
        self.SETTINGS._dev_mode = False
        jwt_token = 'abc123'

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)

    def test_is_jwt_valid__should_succeed_when_provided_bearer_text_in_token(self):
        jwt_body = {'fakeBody': 'valueValue'}
        jwt_token = 'Bearer ' + jwt.encode(jwt_body, self.JWT_SECRET, algorithm='HS256')

        is_jwt_valid(jwt_token)

    @patch('svc.utilities.jwt_utils.datetime')
    def test_create_jwt_token__should_return_a_valid_token(self, mock_date):
        refresh = str(uuid.uuid4())
        now = datetime.now(tz=ZoneInfo('US/Central'))
        mock_date.now.return_value = now
        expected_expiration = now + timedelta(hours=12)
        truncated_expiration = (str(expected_expiration.timestamp() * 1000))[:10]
        user_info = {'user_id': '12345', 'first_name': 'test', 'last_name': 'user', 'roles': ['admin']}
        expected_claims = {'sub': user_info['user_id'],
                               'roles': user_info['roles'],
                               'first_name': user_info['first_name'],
                               'last_name': user_info['last_name'],
                               'refresh_token': refresh,
                               'exp': int(truncated_expiration)}

        actual = create_jwt_token(user_info, refresh)

        assert jwt.decode(actual, self.JWT_SECRET, algorithms='HS256') == expected_claims

    @patch('svc.utilities.jwt_utils.uuid')
    def test_generate_refresh_token__should_return_generated_id(self, mock_uuid):
        refresh = uuid.uuid4()
        mock_uuid.uuid4.return_value = refresh
        actual = generate_refresh_token()

        assert actual == str(refresh)

    def test_is_jwt_valid__should_raise_exception_if_secret_is_not_set(self):
        self.SETTINGS._settings = {'JwtSecret': ''}
        jwt_body = {'fakeBody': 'valueValue'}
        jwt_secret = 'testSecret'
        jwt_token = jwt.encode(jwt_body, jwt_secret, algorithm='HS256')

        with pytest.raises(Unauthorized):
            is_jwt_valid(jwt_token)


@patch('svc.utilities.jwt_utils.PyJWKClient')
@patch('svc.utilities.jwt_utils.jwt')
class TestAuthClient:
    DOMAIN = 'dev-test.us.auth0.com'
    AUDIENCE = 'https://fake.domain.com'
    USER_ID = 'fake_user_id'
    TOKEN = 'IM_A_FAKE_TOKEN'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.Authority._settings = {'Domain': self.DOMAIN, 'Audience': self.AUDIENCE}

    def test_verify_jwt__should_return_decoded_claims(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting']}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)

        actual = client.verify_jwt(self.TOKEN)

        assert actual == claims

    def test_verify_jwt__should_call_jwks_client_with_token(self, mock_jwt, mock_jwks):
        client = AuthClient(self.SETTINGS)

        client.verify_jwt(self.TOKEN)

        mock_jwks.return_value.get_signing_key_from_jwt.assert_called_once_with(self.TOKEN)

    def test_verify_jwt__should_decode_with_signing_key_and_settings(self, mock_jwt, mock_jwks):
        signing_key = mock_jwks.return_value.get_signing_key_from_jwt.return_value
        client = AuthClient(self.SETTINGS)

        client.verify_jwt(self.TOKEN)

        mock_jwt.decode.assert_called_once_with(
            self.TOKEN,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.AUDIENCE,
            issuer=f"https://{self.DOMAIN}/",
        )

    def test_verify_jwt__should_raise_unauthorized_on_invalid_signature(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = InvalidSignatureError()
        client = AuthClient(self.SETTINGS)

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_expired_token(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = ExpiredSignatureError()
        client = AuthClient(self.SETTINGS)

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_decode_error(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = DecodeError()
        client = AuthClient(self.SETTINGS)

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_key_error(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = KeyError()
        client = AuthClient(self.SETTINGS)

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_and_authorize__should_return_claims_when_roles_match(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting', 'security']}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)
        actual = client.verify_and_authorize(self.TOKEN, 'lighting')

        assert actual == claims

    def test_verify_and_authorize__should_return_claims_when_all_required_roles_present(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting', 'security', 'thermostat']}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)
        actual = client.verify_and_authorize(self.TOKEN, 'lighting', 'security')

        assert actual == claims

    def test_verify_and_authorize__should_raise_forbidden_when_role_missing(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting']}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)
        with pytest.raises(Forbidden):
            client.verify_and_authorize(self.TOKEN, 'security')

    def test_verify_and_authorize__should_raise_forbidden_when_roles_claim_missing(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)
        with pytest.raises(Forbidden):
            client.verify_and_authorize(self.TOKEN, 'lighting')

    def test_verify_and_authorize__should_succeed_with_no_required_roles(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': []}
        mock_jwt.decode.return_value = claims
        client = AuthClient(self.SETTINGS)
        actual = client.verify_and_authorize(self.TOKEN)

        assert actual == claims