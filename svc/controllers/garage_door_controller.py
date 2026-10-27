import copy

from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import Automation, AuthClaims, Garage
from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.user_repository import UserRepository
from svc.models.garage import GarageState, GarageOverview
from svc.services import garage_status_service
from svc.services.garage_event_service import GarageEventBroadcaster
from svc.utilities import api_utils
from svc.utilities.auth_utils import AuthClient
from svc.utilities.rabbitmq_client import publish


def get_all_status(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    info = __get_device_info()
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)
    status = api_utils.get_all_garage_doors_status(info.api_key, info.base_url)
    status['doors'] = garage_status_service.build_user_doors(status['doors'], info, preferences.garageAlertTime)
    return GarageOverview.from_dict(status)


def stream_status(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    info = __get_device_info()
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)
    return __status_stream(info, preferences.garageAlertTime)


def update_state(bearer_token, garage_id, request):
    AuthClient.get_instance().verify_jwt(bearer_token)
    garage_open = request.get('garageDoorOpen')
    if garage_open is None:
        raise BadRequest('Field "garageDoorOpen" is required.')
    message = {'id': garage_id, 'action': 'update', 'open': garage_open}
    publish(Automation.GARAGE.QUEUE, message)

    return GarageState(isGarageOpen=garage_open)


def toggle_door(bearer_token, garage_id):
    AuthClient.get_instance().verify_jwt(bearer_token)
    message = {'id': garage_id, 'action': 'toggle'}

    publish(Automation.GARAGE.QUEUE, message)


def schedule_close(bearer_token, garage_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)
    delay_seconds = preferences.garageAlertTime * 60
    message = {'id': garage_id, 'action': 'schedule', 'delay_seconds': delay_seconds}
    publish(Automation.GARAGE.QUEUE, message)


def cancel_scheduled_close(bearer_token, garage_id):
    AuthClient.get_instance().verify_jwt(bearer_token)
    info = __get_device_info()
    api_utils.cancel_garage_schedule(info.api_key, info.base_url, garage_id)


def __get_device_info():
    with DeviceRepository() as database:
        return database.get_device_info('garage_door')


def __status_stream(info, alert_time_minutes):
    broadcaster = GarageEventBroadcaster.get_instance()
    seen_version, status = broadcaster.latest()
    if status is not None:
        yield __format_status_event(status, info, alert_time_minutes)
    while True:
        update = broadcaster.wait_for_update(seen_version, Garage.STREAM_HEARTBEAT_SECONDS)
        if update is None:
            yield ': ping\n\n'
        else:
            seen_version, status = update
            yield __format_status_event(status, info, alert_time_minutes)


def __format_status_event(status, info, alert_time_minutes):
    user_status = copy.deepcopy(status)
    user_status['doors'] = garage_status_service.build_user_doors(user_status['doors'], info, alert_time_minutes)
    overview = GarageOverview.from_dict(user_status)
    return f'event: status\ndata: {overview.to_json()}\n\n'
