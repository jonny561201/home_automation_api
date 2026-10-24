from flask import Response, Blueprint, request, stream_with_context

from svc.constants.home_automation import Mime
from svc.controllers import garage_door_controller


GARAGE_EVENTS_BLUEPRINT = Blueprint('garage_events_blueprint', __name__, url_prefix='/garageDoor')


@GARAGE_EVENTS_BLUEPRINT.route('/events', methods=['GET'])
def stream_garage_door_status():
    bearer_token = request.headers.get('Authorization')
    stream = garage_door_controller.stream_status(bearer_token)
    headers = {'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
    return Response(stream_with_context(stream), status=200, mimetype=Mime.EVENT_STREAM, headers=headers)
