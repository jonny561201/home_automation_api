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
        device_id = database.get_sump_device_id_by_user(user_id)
        current = database.get_current_sump_level_by_device(device_id)
        average = database.get_average_sump_level_by_device(device_id)
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)

        return SumpLevel(
            currentDepth=convert_to_imperial(float(current.distance), preferences.isImperial),
            averageDepth=convert_to_imperial(float(average.distance), preferences.isImperial),
            depthUnit='in' if preferences.isImperial else 'cm',
            warningLevel=current.warning_level,
            latest_date=average.create_day
        )


def save_current_level(api_key: str, request_data: dict):
    with DeviceRepository() as database:
        device_id = database.get_device_id_by_api_key(api_key)
    if api_key is None or device_id is None:
        raise Unauthorized()
    with SumpRepository() as database:
        database.insert_current_sump_level(device_id, request_data)


def save_average_level(api_key: str, request_data: dict):
    with DeviceRepository() as database:
        device_id = database.get_device_id_by_api_key(api_key)
    if api_key is None or device_id is None:
        raise Unauthorized()
    with SumpRepository() as database:
        database.insert_average_sump_level(device_id, request_data)
