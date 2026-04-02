import pytest
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from mock import patch
from werkzeug.exceptions import Unauthorized, Forbidden

from svc.config.settings_state import Settings
from svc.utilities.jwt_utils import AuthClient


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
        try:
            del AuthClient._instance
        except AttributeError:
            pass

    def test_verify_jwt__should_return_decoded_claims(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting']}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()

        actual = client.verify_jwt(self.TOKEN)

        assert actual == claims

    def test_verify_jwt__should_call_jwks_client_with_token(self, mock_jwt, mock_jwks):
        client = AuthClient.get_instance()

        client.verify_jwt(self.TOKEN)

        mock_jwks.return_value.get_signing_key_from_jwt.assert_called_once_with(self.TOKEN)

    def test_verify_jwt__should_decode_with_signing_key_and_settings(self, mock_jwt, mock_jwks):
        signing_key = mock_jwks.return_value.get_signing_key_from_jwt.return_value
        client = AuthClient.get_instance()

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
        client = AuthClient.get_instance()

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_expired_token(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = ExpiredSignatureError()
        client = AuthClient.get_instance()

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_decode_error(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = DecodeError()
        client = AuthClient.get_instance()

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_jwt__should_raise_unauthorized_on_key_error(self, mock_jwt, mock_jwks):
        mock_jwt.decode.side_effect = KeyError()
        client = AuthClient.get_instance()

        with pytest.raises(Unauthorized):
            client.verify_jwt(self.TOKEN)

    def test_verify_and_authorize__should_return_claims_when_roles_match(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting', 'security']}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()
        actual = client.verify_and_authorize(self.TOKEN, 'lighting')

        assert actual == claims

    def test_verify_and_authorize__should_return_claims_when_all_required_roles_present(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting', 'security', 'thermostat']}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()
        actual = client.verify_and_authorize(self.TOKEN, 'lighting', 'security')

        assert actual == claims

    def test_verify_and_authorize__should_raise_forbidden_when_role_missing(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': ['lighting']}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()
        with pytest.raises(Forbidden):
            client.verify_and_authorize(self.TOKEN, 'security')

    def test_verify_and_authorize__should_raise_forbidden_when_roles_claim_missing(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()
        with pytest.raises(Forbidden):
            client.verify_and_authorize(self.TOKEN, 'lighting')

    def test_verify_and_authorize__should_succeed_with_no_required_roles(self, mock_jwt, mock_jwks):
        claims = {'sub': self.USER_ID, 'roles': []}
        mock_jwt.decode.return_value = claims
        client = AuthClient.get_instance()
        actual = client.verify_and_authorize(self.TOKEN)

        assert actual == claims