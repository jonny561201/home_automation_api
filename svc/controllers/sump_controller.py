from svc.constants.home_automation import AuthClaims
from svc.db.repositories.sump_repository import SumpDatabase
from svc.models.sump import SumpLevel
from svc.utilities.conversion_utils import convert_to_imperial
from svc.utilities.jwt_utils import AuthClient


def get_sump_level(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with SumpDatabase() as database:
        current_data = database.get_current_sump_level_by_user(user_id)
        average_data = database.get_average_sump_level_by_user(user_id)
        preferences = database.get_preferences_by_user(user_id)

        return __map_response(current_data, average_data, preferences.isImperial)


def save_current_level(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with SumpDatabase() as database:
        database.insert_current_sump_level(user_id, request_data)


def __map_response(current_data, average_data, is_imperial):
    return SumpLevel(
        currentDepth=convert_to_imperial(current_data.get('currentDepth'), is_imperial),
        averageDepth=convert_to_imperial(average_data.get('averageDepth'), is_imperial),
        depthUnit='in' if is_imperial else 'cm',
        warningLevel=current_data.get('warningLevel'),
        latest_date=average_data.get('latestDate')
    )