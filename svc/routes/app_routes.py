import json

from flask import Blueprint, request, Response
from flask_cors import cross_origin
from werkzeug.exceptions import Unauthorized

from svc.constants.home_automation import DEFAULT_HEADERS
from svc.controllers import app_controller

APP_BLUEPRINT = Blueprint('app_routes', __name__)


@APP_BLUEPRINT.route('/healthCheck')
def health_check():
    return "Success"


@APP_BLUEPRINT.route('/token', methods=['POST'])
@cross_origin(origin='*')
def get_token():
    body = json.loads(request.data)
    if body['grant_type'] == 'client_credentials':
        token = app_controller.get_login(body['client_id'], body['client_secret'])
    elif body['grant_type'] == 'refresh_token':
        token = app_controller.refresh_bearer_token(body['refresh_token'])
    else:
        raise Unauthorized()
    return Response(json.dumps({'bearerToken': token.decode('UTF-8')}), status=200, headers=DEFAULT_HEADERS)


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


@APP_BLUEPRINT.route('/userId/<user_id>/tasks', defaults={'task_type': None}, methods=['GET'])
@APP_BLUEPRINT.route('/userId/<user_id>/tasks/<task_type>', methods=['GET'])
def get_user_tasks_by_user_id(user_id, task_type):
    bearer_token = request.headers.get('Authorization')
    tasks = app_controller.get_user_tasks(bearer_token, user_id, task_type)
    return Response(json.dumps(tasks), status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/tasks/<task_id>', methods=['DELETE'])
def delete_user_tasks_by_user_id(user_id, task_id):
    bearer_token = request.headers.get('Authorization')
    app_controller.delete_user_task(bearer_token, user_id, task_id)
    return Response(status=200, headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/tasks', methods=['POST'])
def insert_user_task_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    updated_tasks = app_controller.insert_user_task(bearer_token, user_id, request.data)
    return Response(json.dumps(updated_tasks), status=200,  headers=DEFAULT_HEADERS)


@APP_BLUEPRINT.route('/userId/<user_id>/tasks/update', methods=['POST'])
def update_user_task_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    task = app_controller.update_user_task(bearer_token, user_id, request.data)
    return Response(json.dumps(task), status=200, headers=DEFAULT_HEADERS)