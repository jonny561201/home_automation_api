import json

from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers import push_notification_controller


PUSH_BLUEPRINT = Blueprint('push_routes', __name__, url_prefix='/notifications')


@PUSH_BLUEPRINT.route('/vapid-key', methods=['GET'])
def vapid_key():
    response = push_notification_controller.get_vapid_public_key()
    return Response(json.dumps(response), status=200, mimetype=Mime.JSON)


@PUSH_BLUEPRINT.route('/subscribe', methods=['POST'])
def subscribe():
    bearer_token = request.headers.get('Authorization')
    push_notification_controller.subscribe_user(bearer_token, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)


@PUSH_BLUEPRINT.route('/subscribe', methods=['DELETE'])
def unsubscribe():
    bearer_token = request.headers.get('Authorization')
    push_notification_controller.unsubscribe_user(bearer_token, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)
