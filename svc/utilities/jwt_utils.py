import uuid
from datetime import timedelta, datetime

import jwt
import pytz
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from werkzeug.exceptions import Unauthorized

from svc.constants.settings_state import Settings


def is_jwt_valid(jwt_token):
    if jwt_token is None:
        raise Unauthorized
    _parse_jwt_token(jwt_token)


def create_jwt_token(user_info, refresh_token):
    expire_time = datetime.now(tz=pytz.timezone('US/Central')) + timedelta(hours=12)
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
