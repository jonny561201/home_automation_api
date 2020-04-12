import json

from flask import request
from svc.controllers.devices_controller import add_device_to_role


def add_device_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    request_data = json.loads(request.data.decode('UTF-8'))
    add_device_to_role(bearer_token, user_id, request_data)
