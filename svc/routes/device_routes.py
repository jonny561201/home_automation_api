import json

from flask import request, Response
from svc.controllers.devices_controller import add_device_to_role


DEFAULT_HEADERS = {'Content-Type': 'text/json'}

def add_device_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    request_data = json.loads(request.data.decode('UTF-8'))
    add_device_to_role(bearer_token, user_id, request_data)
    return Response(status=200, headers=DEFAULT_HEADERS)
