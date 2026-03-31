from flask import request, Response, Blueprint

from svc.constants.home_automation import Mime
from svc.controllers import devices_controller


DEVICES_BLUEPRINT = Blueprint('devices_routes', __name__, url_prefix='/devices')


@DEVICES_BLUEPRINT.route('/register', methods=['POST'])
def add_device():
    bearer_token = request.headers.get('Authorization')
    device = devices_controller.add_device_to_role(bearer_token, request.get_json())
    return Response(device.to_json(), status=200, mimetype=Mime.JSON)


@DEVICES_BLUEPRINT.route('/<device_id>/node', methods=['POST'])
def add_device_node(device_id):
    bearer_token = request.headers.get('Authorization')
    remaining_devices = devices_controller.add_node_to_device(bearer_token, device_id, request.get_json())
    return Response(remaining_devices.to_json(), status=200, mimetype=Mime.JSON)
