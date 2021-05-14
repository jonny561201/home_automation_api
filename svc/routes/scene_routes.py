from flask import request, Response

from svc.controllers.scene_controller import get_created_scenes


def get_scenes_by_user(user_id):
    bearer_token = request.headers.get('Authorization')
    get_created_scenes(bearer_token, user_id)
    return Response(status=200)
