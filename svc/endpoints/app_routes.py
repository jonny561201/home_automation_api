from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers import app_controller

APP_BLUEPRINT = Blueprint('app_routes', __name__)


@APP_BLUEPRINT.route('/healthCheck')
def health_check():
    return Response("Success", status=200)


@APP_BLUEPRINT.route('/resetPassword', methods=['POST'])
def reset_user_password():
    bearer_token = request.headers.get('Authorization')
    app_controller.reset_password(bearer_token)
    return Response(status=204, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/preferences', methods=['GET'])
def get_user_preferences():
    bearer_token = request.headers.get('Authorization')
    preferences = app_controller.get_user_preferences(bearer_token)
    return Response(preferences.to_json(), status=200, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/preferences/update', methods=['POST'])
def update_user_preferences():
    bearer_token = request.headers.get('Authorization')
    app_controller.save_user_preferences(bearer_token, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/tasks', defaults={'task_type': None}, methods=['GET'])
@APP_BLUEPRINT.route('/tasks/<task_type>', methods=['GET'])
def get_user_tasks(task_type):
    bearer_token = request.headers.get('Authorization')
    tasks = app_controller.get_user_tasks(bearer_token, task_type)
    return Response(tasks.to_json(), status=200, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/tasks/<task_id>', methods=['DELETE'])
def delete_user_task(task_id):
    bearer_token = request.headers.get('Authorization')
    app_controller.delete_user_task(bearer_token, task_id)
    return Response(status=200, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/tasks', methods=['POST'])
def insert_user_task():
    bearer_token = request.headers.get('Authorization')
    updated_tasks = app_controller.insert_user_task(bearer_token, request.get_json())
    return Response(updated_tasks.to_json(), status=200, mimetype=Mime.JSON)


@APP_BLUEPRINT.route('/tasks/update', methods=['POST'])
def update_user_task():
    bearer_token = request.headers.get('Authorization')
    task = app_controller.update_user_task(bearer_token, request.get_json())
    return Response(task.to_json(), status=200, mimetype=Mime.JSON)
