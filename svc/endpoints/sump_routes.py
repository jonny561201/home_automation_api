from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers.sump_controller import get_sump_level, get_depth_history, get_daily_averages, save_current_level, save_average_level


SUMP_BLUEPRINT = Blueprint('sump_pump_blueprint', __name__, url_prefix='/sumpPump')


@SUMP_BLUEPRINT.route('/depth', methods=['GET'])
def get_current_sump_level():
    bearer_token = request.headers.get('Authorization')
    depth = get_sump_level(bearer_token)
    return Response(depth.to_json(), status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/depth/history', methods=['GET'])
def get_sump_depth_history():
    bearer_token = request.headers.get('Authorization')
    readings = get_depth_history(bearer_token)
    return Response(readings.to_json(), status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/depth/daily', methods=['GET'])
def get_sump_daily_averages():
    bearer_token = request.headers.get('Authorization')
    days = request.args.get('days', 7, type=int)
    readings = get_daily_averages(bearer_token, days)
    return Response(readings.to_json(), status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/currentDepth', methods=['POST'])
def save_current_depth():
    api_key = request.headers.get('X-API-Key')
    save_current_level(api_key, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)


@SUMP_BLUEPRINT.route('/averageDepth', methods=['POST'])
def save_average_depth():
    api_key = request.headers.get('X-API-Key')
    save_average_level(api_key, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)
