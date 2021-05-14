import json

from flask import request, Response, Blueprint

from svc.controllers import scene_controller


SCENE_BLUEPRINT = Blueprint('scene_routes', __name__, url_prefix='/scenes')
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@SCENE_BLUEPRINT.route('/userId/<user_id>', methods=['GET'])
def get_scenes_by_user(user_id):
    bearer_token = request.headers.get('Authorization')
    scenes = scene_controller.get_created_scenes(bearer_token, user_id)
    return Response(json.dumps(scenes), status=200, headers=DEFAULT_HEADERS)


def delete_scene_by_user(user_id, scene_id):
    bearer_token = request.headers['Authorization']
    scene_controller.delete_created_scene(bearer_token, None, None)
