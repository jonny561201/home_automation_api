import base64
import os
from datetime import timedelta, datetime

import jwt
import pytz
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from werkzeug.exceptions import Unauthorized, BadRequest
from svc.constants.settings_state import Settings


def is_jwt_valid(jwt_token):
    if jwt_token is None:
        raise Unauthorized
    _parse_jwt_token(jwt_token)


def create_jwt_token(user_id):
    expire_time = datetime.now(tz=pytz.timezone('US/Central')) + timedelta(hours=2)
    settings = Settings.get_instance().get_settings()
    jwt_secret = settings.get('DevJwtSecret') if settings.get('Development') else os.environ['JWT_SECRET']
    return jwt.encode({'user_id': user_id, 'exp': expire_time}, jwt_secret, algorithm='HS256')


def extract_credentials(bearer_token):
    if bearer_token is None or bearer_token == '':
        raise BadRequest
    encoded_token = bearer_token.replace('Basic ', '')
    decoded_token = base64.b64decode(encoded_token).decode('UTF-8')

    credentials = decoded_token.split(':')
    return credentials[0], credentials[1]


def _parse_jwt_token(jwt_token):
    try:
        stripped_token = jwt_token.replace('Bearer ', '')
        settings = Settings.get_instance().get_settings()
        jwt_secret = settings.get('DevJwtSecret') if settings.get('Development') else os.environ['JWT_SECRET']
        jwt.decode(stripped_token, jwt_secret, algorithms=["HS256"])
    except (InvalidSignatureError, ExpiredSignatureError, DecodeError, KeyError) as er:
        raise Unauthorized
