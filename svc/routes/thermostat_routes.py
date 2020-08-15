from flask import Blueprint, request, Response

from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature

THERMOSTAT_BLUEPRINT = Blueprint('thermostat_blueprint', __name__, url_prefix='/thermostat')
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@THERMOSTAT_BLUEPRINT.route('/temperature/<user_id>', methods=['GET'])
def get_temperature(user_id):
    bearer_token = request.headers.get('Authorization')
    return get_user_temp(user_id, bearer_token)


@THERMOSTAT_BLUEPRINT.route('/temperature/<user_id>', methods=['POST'])
def set_temperature(user_id):
    bearer_token = request.headers.get('Authorization')
    set_user_temperature(request.data, bearer_token)
    return Response(status=200, headers=DEFAULT_HEADERS)

