from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.jwt_utils import is_jwt_valid


def get_created_scenes(bearer_token, user_id):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        database.get_scenes_by_user(user_id)
