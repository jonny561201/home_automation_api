import json

from flask import request, Response, Blueprint

from svc.controllers.scene_controller import get_created_scenes


SCENE_BLUEPRINT = Blueprint('scene_routes', __name__, url_prefix='/scenes')
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@SCENE_BLUEPRINT.route('/userId/<user_id>', methods=['GET'])
def get_scenes_by_user(user_id):
    bearer_token = request.headers.get('Authorization')
    scenes = get_created_scenes(bearer_token, user_id)
    return Response(json.dumps(scenes), status=200, headers=DEFAULT_HEADERS)
