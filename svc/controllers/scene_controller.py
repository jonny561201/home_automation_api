from svc.constants.home_automation import AuthClaims
from svc.db.repositories.lights_repository import LightsRepository
from svc.utilities.auth_utils import AuthClient


def get_created_scenes(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with LightsRepository() as database:
        return database.get_scenes_by_user(user_id)


def create_scene(bearer_token, request):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with LightsRepository() as database:
        return database.create_scene(user_id, request)


def delete_created_scene(bearer_token, scene_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with LightsRepository() as database:
        database.delete_scene_by_user(user_id, scene_id)
