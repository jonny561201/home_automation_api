import json

from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers import geocode_controller


GEOCODE_BLUEPRINT = Blueprint('geocode_routes', __name__, url_prefix='/geocode')


@GEOCODE_BLUEPRINT.route('/reverse', methods=['GET'])
def reverse_geocode():
    bearer_token = request.headers.get('Authorization')
    latitude = request.args.get('latitude', type=float)
    longitude = request.args.get('longitude', type=float)
    location = geocode_controller.reverse_geocode(bearer_token, latitude, longitude)
    return Response(json.dumps(location), status=200, mimetype=Mime.JSON)
