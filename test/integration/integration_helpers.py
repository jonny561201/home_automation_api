import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from mock import MagicMock

from constants.home_automation import AuthClaims
from svc.config.settings_state import Settings
from svc.utilities.jwt_utils import AuthClient


def mock_jwks_token(user_id: str):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    domain = 'dev-test.us.auth0.com'
    audience = 'http://localhost:5000'
    claims = {AuthClaims.USER_ID: user_id, 'aud': audience, 'iss': f'https://{domain}/'}
    settings = Settings.get_instance()
    settings.Authority._settings = {'Domain': domain, 'Audience': audience}

    auth_client = AuthClient.get_instance()
    auth_client.jwks_client = MagicMock()
    mock_signing_key = MagicMock()
    mock_signing_key.key = public_key
    auth_client.jwks_client.get_signing_key_from_jwt.return_value = mock_signing_key

    return jwt.encode(claims, private_key, algorithm='RS256', headers={'kid': 'test-key-id'})
