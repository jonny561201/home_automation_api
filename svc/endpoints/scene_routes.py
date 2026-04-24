from flask import request, Response, Blueprint

from svc.constants.home_automation import Mime
from svc.controllers import scene_controller


SCENE_BLUEPRINT = Blueprint('scene_routes', __name__, url_prefix='/scenes')


@SCENE_BLUEPRINT.route('', methods=['POST'])
def create_scene():
    bearer_token = request.headers.get('Authorization')
    scene_controller.create_scene(bearer_token, request.get_json())
    return Response(status=200, mimetype=Mime.JSON)


@SCENE_BLUEPRINT.route('/list', methods=['GET'])
def get_scenes():
    bearer_token = request.headers.get('Authorization')
    scenes = scene_controller.get_created_scenes(bearer_token)
    return Response(scenes.to_json(), status=200, mimetype=Mime.JSON)


@SCENE_BLUEPRINT.route('/<scene_id>', methods=['DELETE'])
def delete_scene(scene_id):
    bearer_token = request.headers.get('Authorization')
    scene_controller.delete_created_scene(bearer_token, scene_id)
    return Response(status=200, mimetype=Mime.JSON)
