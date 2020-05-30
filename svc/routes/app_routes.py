import json

from flask import Blueprint, request, Response

from svc.controllers import app_controller

APP_BLUEPRINT = Blueprint('app_routes', __name__)
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@APP_BLUEPRINT.route('/healthCheck')
def health_check():
    return "Success"


@APP_BLUEPRINT.route('/login', methods=['GET'])
def app_login():
    basic_token = request.headers.get('Authorization')
    jwt_token = app_controller.get_login(basic_token)
    return Response(json.dumps({'bearerToken': jwt_token.decode('UTF-8')}), status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/preferences', methods=['GET'])
def get_user_preferences_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    preferences = app_controller.get_user_preferences(bearer_token, user_id)
    return Response(json.dumps(preferences), status=200)


@APP_BLUEPRINT.route('/userId/<user_id>/preferences/update', methods=['POST'])
def update_user_preferences_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    app_controller.save_user_preferences(bearer_token, user_id, request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/updateAccount', methods=['POST'])
def update_user_password(user_id):
    bearer_token = request.headers.get('Authorization')
    app_controller.change_password(bearer_token, user_id,  request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/roles', methods=['GET'])
def get_roles_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    roles = app_controller.get_roles(bearer_token, user_id)
    return Response(json.dumps(roles), status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/createChildAccount', methods=['POST'])
def post_child_account_by_user(user_id):
    bearer_token = request.headers.get('Authorization')
    app_controller.create_child_account_by_user(bearer_token, user_id, request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)
