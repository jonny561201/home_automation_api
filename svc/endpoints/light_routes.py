import json

from flask import request, Response, Blueprint

from svc.constants.home_automation import Mime
from svc.controllers import light_controller


LIGHT_BLUEPRINT = Blueprint('light_blueprint', __name__, url_prefix="/lights")


@LIGHT_BLUEPRINT.route('/groups', methods=['GET'])
def get_assigned_light_groups():
    bearer_token = request.cookies.get('access_token')
    response = light_controller.get_assigned_light_groups(bearer_token)

    return Response(json.dumps(response), status=200, mimetype=Mime.JSON)


@LIGHT_BLUEPRINT.route('/group/state', methods=['POST'])
def set_assigned_light_group():
    bearer_token = request.cookies.get('access_token')
    light_controller.set_assigned_light_groups(bearer_token, request.get_json())

    return Response(status=200, mimetype=Mime.JSON)


@LIGHT_BLUEPRINT.route('/group/light', methods=['POST'])
def set_light_state():
    bearer_token = request.cookies.get('access_token')
    light_controller.set_assigned_light(bearer_token, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)


@LIGHT_BLUEPRINT.route('/unregistered', methods=['GET'])
def get_unregistered_devices():
    bearer_token = request.cookies.get('access_token')
    lights = light_controller.get_unassigned_lights(bearer_token)

    return Response(json.dumps(lights), status=200, mimetype=Mime.JSON)


@LIGHT_BLUEPRINT.route('/register', methods=['POST'])
def register_unassigned_light():
    bearer_token = request.cookies.get('access_token')
    light_controller.register_unassigned_light(bearer_token, request.get_json())

    return Response(status=200, mimetype=Mime.JSON)
