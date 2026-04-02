from svc.db.repositories.lights_repository import LightsRepository
from svc.utilities.jwt_utils import AuthClient


def get_created_scenes(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims['https://soaringleafsolutions.com/user_id']
    with LightsRepository() as database:
        return database.get_scenes_by_user(user_id)


def delete_created_scene(bearer_token, scene_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims['https://soaringleafsolutions.com/user_id']
    with LightsRepository() as database:
        database.delete_scene_by_user(user_id, scene_id)
