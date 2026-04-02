import jwt
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError, PyJWKClient
from werkzeug.exceptions import Unauthorized, Forbidden

from svc.config.settings_state import Settings
from svc.config.singleton import Singleton


@Singleton
class AuthClient:
    ALGORITHMS = ["RS256"]

    def __init__(self):
        self.settings = Settings.get_instance()
        jwks_url = f"https://{self.settings.Authority.domain}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(jwks_url)

    def verify_jwt(self, token: str):
        try:
            stripped_token = token.replace('Bearer ', '')
            signing_key = self.jwks_client.get_signing_key_from_jwt(stripped_token)
            return jwt.decode(
                stripped_token,
                signing_key.key,
                algorithms=self.ALGORITHMS,
                audience=self.settings.Authority.audience,
                issuer=f"https://{self.settings.Authority.domain}/",
            )
        except (InvalidSignatureError, ExpiredSignatureError, DecodeError, KeyError, Exception) as e:
            raise Unauthorized()

    def verify_and_authorize(self, token: str, *required_roles: str):
        claims = self.verify_jwt(token)
        user_roles = set(claims.get('roles', []))
        if not set(required_roles).issubset(user_roles):
            raise Forbidden()

        return claims
