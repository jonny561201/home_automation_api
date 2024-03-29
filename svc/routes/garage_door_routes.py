from flask import Response, Blueprint
from flask import json
from flask import request

from svc.constants.home_automation import DEFAULT_HEADERS
from svc.controllers import garage_door_controller

GARAGE_BLUEPRINT = Blueprint('garage_blueprint', __name__, url_prefix='/garageDoor')


@GARAGE_BLUEPRINT.route('/<garage_id>/user/<user_id>/status', methods=['GET'])
def get_garage_door_status(user_id, garage_id):
    bearer_token = request.headers.get('Authorization')
    status = garage_door_controller.get_status(bearer_token, user_id, garage_id)
    return Response(json.dumps(status), status=200, headers=DEFAULT_HEADERS)


@GARAGE_BLUEPRINT.route('/<garage_id>/user/<user_id>/state', methods=['POST'])
def update_garage_door_state(user_id, garage_id):
    bearer_token = request.headers.get('Authorization')
    updated_state = garage_door_controller.update_state(bearer_token, user_id, garage_id, request.data)
    return Response(json.dumps(updated_state), status=200, headers=DEFAULT_HEADERS)


@GARAGE_BLUEPRINT.route('/<garage_id>/user/<user_id>/toggle', methods=['GET'])
def toggle_garage_door(user_id, garage_id):
    bearer_token = request.headers.get('Authorization')
    garage_door_controller.toggle_door(bearer_token, user_id, garage_id)
    return Response(status=200, headers=DEFAULT_HEADERS)
