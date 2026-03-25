from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers.sump_controller import get_sump_level, save_current_level


SUMP_BLUEPRINT = Blueprint('sump_pump_blueprint', __name__, url_prefix='/sumpPump')


@SUMP_BLUEPRINT.route('/depth', methods=['GET'])
def get_current_sump_level():
    bearer_token = request.headers.get('Authorization')
    depth = get_sump_level(bearer_token)
    return Response(depth.to_json(), status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/currentDepth', methods=['POST'])
def save_current_depth():
    bear_token = request.headers.get('Authorization')
    save_current_level(bear_token, request.get_json())
