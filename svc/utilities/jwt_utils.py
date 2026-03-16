import uuid
from datetime import timedelta, datetime

import jwt
from zoneinfo import ZoneInfo
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError, PyJWKClient
from werkzeug.exceptions import Unauthorized

from svc.config.settings_state import Settings


def is_jwt_valid(jwt_token):
    if jwt_token is None:
        raise Unauthorized
    _parse_jwt_token(jwt_token)


def create_jwt_token(user_info, refresh_token):
    expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(hours=12)
    settings = Settings.get_instance()
    return jwt.encode({'user': user_info,
                       'refresh_token': refresh_token,
                       'exp': expire_time}, settings.jwt_secret, algorithm='HS256')


def generate_refresh_token():
    return str(uuid.uuid4())


def _parse_jwt_token(jwt_token):
    try:
        stripped_token = jwt_token.replace('Bearer ', '')
        settings = Settings.get_instance()
        jwt.decode(stripped_token, settings.jwt_secret, algorithms=["HS256"])
    except (InvalidSignatureError, ExpiredSignatureError, DecodeError, KeyError) as er:
        raise Unauthorized



#TODO: add a has_permission method that validates and checks for claim?
class AuthClient:
    ALGORITHMS = ["RS256"]

    def __init__(self, settings: Settings):
        self.settings = settings
        jwks_url = f"https://{self.settings.Authority.domain}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(jwks_url)

    def verify_jwt(self, token: str):
        signing_key = self.jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=self.ALGORITHMS,
            audience=self.settings.Authority.audience,
            issuer=f"https://{self.settings.Authority.domain}/",
        )

        return payload
