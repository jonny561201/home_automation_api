from flask import Response, Blueprint
from flask import request

from svc.constants.home_automation import Mime
from svc.controllers import garage_door_controller


GARAGE_BLUEPRINT = Blueprint('garage_blueprint', __name__, url_prefix='/garageDoor')


@GARAGE_BLUEPRINT.route('/<garage_id>/status', methods=['GET'])
def get_garage_door_status(garage_id):
    bearer_token = request.cookies.get('access_token')
    status = garage_door_controller.get_status(bearer_token, garage_id)
    return Response(status.to_json(), status=200, mimetype=Mime.JSON)


@GARAGE_BLUEPRINT.route('/<garage_id>/state', methods=['POST'])
def update_garage_door_state(garage_id):
    bearer_token = request.cookies.get('access_token')
    updated_state = garage_door_controller.update_state(bearer_token, garage_id, request.get_json())
    return Response(updated_state.to_json(), status=200, mimetype=Mime.JSON)


@GARAGE_BLUEPRINT.route('/<garage_id>/toggle', methods=['GET'])
def toggle_garage_door(garage_id):
    bearer_token = request.cookies.get('access_token')
    garage_door_controller.toggle_door(bearer_token, garage_id)
    return Response(status=200, mimetype=Mime.JSON)
