import json

from flask import request, Response, Blueprint
from svc.controllers import devices_controller


DEVICES_BLUEPRINT = Blueprint('devices_routes', __name__)
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@DEVICES_BLUEPRINT.route('/userId/<user_id>/devices', methods=['POST'])
def add_device_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    request_data = json.loads(request.data.decode('UTF-8'))
    device_id = devices_controller.add_device_to_role(bearer_token, user_id, request_data)
    return Response(json.dumps({'deviceId': device_id}), status=200, headers=DEFAULT_HEADERS)


@DEVICES_BLUEPRINT.route('/userId/<user_id>/devices/<device_id>/node', methods=['POST'])
def add_device_node_by_user_id(user_id, device_id):
    bearer_token = request.headers.get('Authorization')
    request_data = json.loads(request.data.decode('UTF-8'))
    remaining_devices = devices_controller.add_node_to_device(bearer_token, user_id, device_id, request_data)
    return Response(json.dumps(remaining_devices), status=200, headers=DEFAULT_HEADERS)
