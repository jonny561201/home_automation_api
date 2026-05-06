from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers import thermostat_controller


THERMOSTAT_BLUEPRINT = Blueprint('thermostat_blueprint', __name__, url_prefix='/thermostat')


@THERMOSTAT_BLUEPRINT.route('/temperature', methods=['GET'])
def get_temperature():
    bearer_token = request.headers.get('Authorization')
    temp = thermostat_controller.get_user_temp(bearer_token)
    return Response(temp.to_json(), status=200, mimetype=Mime.JSON)


@THERMOSTAT_BLUEPRINT.route('/temperature/desired', methods=['POST'])
def set_desired_temperature():
    bearer_token = request.headers.get('Authorization')
    thermostat_controller.set_user_temperature(request.get_json(), bearer_token)
    return Response(status=200, mimetype=Mime.JSON)


@THERMOSTAT_BLUEPRINT.route('/forecast', methods=['GET'])
def get_forecast_data():
    bearer_token = request.headers.get('Authorization')
    forecast = thermostat_controller.get_user_forecast(bearer_token)
    return Response(forecast.to_json(), status=200, mimetype=Mime.JSON)


@THERMOSTAT_BLUEPRINT.route('/forecast/extended', methods=['GET'])
def get_extended_forecast_data():
    bearer_token = request.headers.get('Authorization')
    forecast = thermostat_controller.get_user_extended_forecast(bearer_token)
    return Response(forecast.to_json(), status=200, mimetype=Mime.JSON)
