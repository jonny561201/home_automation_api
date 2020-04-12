import json

from flask import request, Response, Blueprint
from svc.controllers.devices_controller import add_device_to_role


DEVICES_BLUEPRINT = Blueprint('devices_routes', __name__)
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@DEVICES_BLUEPRINT.route('/userId/<user_id>/devices', methods=['POST'])
def add_device_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    request_data = json.loads(request.data.decode('UTF-8'))
    add_device_to_role(bearer_token, user_id, request_data)
    return Response(status=200, headers=DEFAULT_HEADERS)
