import json

from models.sump import SumpLevel
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.utilities.conversion_utils import convert_to_imperial
from svc.utilities.jwt_utils import is_jwt_valid


def get_sump_level(user_id, bearer_token):
    is_jwt_valid(bearer_token)
    with UserDatabaseManager() as database:
        current_data = database.get_current_sump_level_by_user(user_id)
        average_data = database.get_average_sump_level_by_user(user_id)
        preferences = database.get_preferences_by_user(user_id)

        return __map_response(current_data, average_data, preferences['is_imperial'])


def save_current_level(user_id, bearer_token, request):
    is_jwt_valid(bearer_token)
    depth_info = json.loads(request)
    with UserDatabaseManager() as database:
        database.insert_current_sump_level(user_id, depth_info)


def __map_response(current_data, average_data, is_imperial):
    return SumpLevel(
        currentDepth=convert_to_imperial(current_data.get('currentDepth'), is_imperial),
        averageDepth=convert_to_imperial(average_data.get('averageDepth'), is_imperial),
        depthUnit='in' if is_imperial else 'cm',
        warningLevel=current_data.get('warningLevel'),
        latest_date=average_data.get('latestDate')
    )