import json

from flask import Blueprint, request, Response

from svc.constants.home_automation import DEFAULT_HEADERS
from svc.controllers import thermostat_controller

THERMOSTAT_BLUEPRINT = Blueprint('thermostat_blueprint', __name__, url_prefix='/thermostat')


@THERMOSTAT_BLUEPRINT.route('/temperature/<user_id>', methods=['GET'])
def get_temperature(user_id):
    bearer_token = request.headers.get('Authorization')
    return thermostat_controller.get_user_temp(user_id, bearer_token)


@THERMOSTAT_BLUEPRINT.route('/temperature/<user_id>', methods=['POST'])
def set_temperature(user_id):
    bearer_token = request.headers.get('Authorization')
    thermostat_controller.set_user_temperature(request.data, bearer_token)
    return Response(status=200, headers=DEFAULT_HEADERS)


def get_forecast_data(user_id):
    bearer_token = request.headers.get('Authorization')
    forecast = thermostat_controller.get_user_forecast(user_id, bearer_token)
    return Response(json.dumps(forecast), status=200, headers=DEFAULT_HEADERS)
