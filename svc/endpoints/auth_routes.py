import json

from flask import Blueprint, request, Response

from svc.config.settings_state import Settings
from svc.constants.home_automation import Mime
from svc.controllers import auth_controller

AUTH_BLUEPRINT = Blueprint('auth_routes', __name__, url_prefix='/token')


@AUTH_BLUEPRINT.route('/exchange', methods=['POST'])
def exchange_token():
    tokens = auth_controller.exchange_auth_code(request.get_json())
    settings = Settings.get_instance()
    is_secure = settings.environment != 'local'
    response = Response(status=200, mimetype=Mime.JSON)
    response.set_cookie('access_token', tokens['access_token'], httponly=True, secure=is_secure, samesite='Strict', max_age=tokens.get('expires_in', 86400))
    response.set_cookie('refresh_token', tokens['refresh_token'], httponly=True, secure=is_secure, samesite='Strict', path='/token', max_age=60 * 60 * 24 * 30)

    return response


@AUTH_BLUEPRINT.route('/provision', methods=['POST'])
def provision_user():
    api_key = request.headers.get('X-API-Key')
    user_id = auth_controller.provision_user(api_key, request.get_json())
    return Response(json.dumps({'user_id': user_id}), status=201, mimetype=Mime.JSON)
