import json

from flask import Blueprint, request, Response

from svc.controllers.app_controller import get_login, get_user_preferences

APP_BLUEPRINT = Blueprint('app_routes', __name__)
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@APP_BLUEPRINT.route('/healthCheck')
def health_check():
    return "Success"


# TODO: Login should return role
@APP_BLUEPRINT.route('/login', methods=['GET'])
def app_login():
    basic_token = request.headers.get('Authorization')
    jwt_token = get_login(basic_token)
    return Response(json.dumps({'bearerToken': jwt_token.decode('UTF-8')}), status=200, headers=DEFAULT_HEADERS)


# TODO: create set preferences page
def get_user_preferences_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    get_user_preferences(bearer_token, user_id)
