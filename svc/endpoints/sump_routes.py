from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers.sump_controller import get_sump_level, save_current_level

SUMP_BLUEPRINT = Blueprint('sump_pump_blueprint', __name__, url_prefix='/sumpPump')


@SUMP_BLUEPRINT.route('/user/<user_id>/depth', methods=['GET'])
def get_current_sump_level(user_id):
    bearer_token = request.headers.get('Authorization')
    depth = get_sump_level(user_id, bearer_token)
    return Response(depth.to_json(), status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/user/<user_id>/currentDepth', methods=['POST'])
def save_current_level_by_user(user_id):
    bear_token = request.headers.get('Authorization')
    depth_info = request.data
    save_current_level(user_id, bear_token, depth_info)

