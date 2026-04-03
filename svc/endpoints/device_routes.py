from flask import request, Response, Blueprint

from svc.constants.home_automation import Mime
from svc.controllers import devices_controller


DEVICES_BLUEPRINT = Blueprint('devices_routes', __name__, url_prefix='/devices')


@DEVICES_BLUEPRINT.route('/register', methods=['POST'])
def add_device():
    bearer_token = request.headers.get('Authorization')
    device = devices_controller.add_device(bearer_token, request.get_json())
    return Response(device.to_json(), status=200, mimetype=Mime.JSON)


@DEVICES_BLUEPRINT.route('/devices', methods=['GET'])
def get_devices():
    bearer_token = request.headers.get('Authorization')
    devices = devices_controller.get_user_devices(bearer_token)
    return Response(devices.to_json(), status=200, mimetype=Mime.JSON)