from werkzeug.exceptions import Unauthorized

from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.user_repository import UserRepository
from svc.constants.home_automation import AuthClaims
from svc.db.repositories.sump_repository import SumpRepository
from svc.models.sump import SumpLevel
from svc.utilities.conversion_utils import convert_to_imperial
from svc.utilities.auth_utils import AuthClient


def get_sump_level(bearer_token: str):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with SumpRepository() as database:
        current_data = database.get_current_sump_level_by_user(user_id)
        average_data = database.get_average_sump_level_by_user(user_id)
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)

        return __map_response(current_data, average_data, preferences.isImperial)


def save_current_level(api_key: str, request_data: dict):
    with DeviceRepository() as database:
        user_id = database.get_user_id_by_device_api_key(api_key)
    if api_key is None or user_id is None:
        raise Unauthorized()
    with SumpRepository() as database:
        database.insert_current_sump_level(user_id, request_data)


def __map_response(current_data, average_data, is_imperial):
    return SumpLevel(
        currentDepth=convert_to_imperial(current_data.get('currentDepth'), is_imperial),
        averageDepth=convert_to_imperial(average_data.get('averageDepth'), is_imperial),
        depthUnit='in' if is_imperial else 'cm',
        warningLevel=current_data.get('warningLevel'),
        latest_date=average_data.get('latestDate')
    )
