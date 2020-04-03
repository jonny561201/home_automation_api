import json

from flask import Blueprint, request, Response

from svc.controllers.app_controller import get_login, get_user_preferences, save_user_preferences

APP_BLUEPRINT = Blueprint('app_routes', __name__)
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@APP_BLUEPRINT.route('/healthCheck')
def health_check():
    return "Success"


@APP_BLUEPRINT.route('/login', methods=['GET'])
def app_login():
    basic_token = request.headers.get('Authorization')
    jwt_token = get_login(basic_token)
    return Response(json.dumps({'bearerToken': jwt_token.decode('UTF-8')}), status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/preferences', methods=['GET'])
def get_user_preferences_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    preferences = get_user_preferences(bearer_token, user_id)
    return Response(json.dumps(preferences), status=200)


@APP_BLUEPRINT.route('/userId/<user_id>/preferences/update', methods=['POST'])
def update_user_preferences_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    save_user_preferences(bearer_token, user_id, request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)
