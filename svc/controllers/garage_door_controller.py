from werkzeug.exceptions import BadRequest, FailedDependency

from svc.db.repositories.device_repository import DeviceRepository
from svc.constants.home_automation import Automation, AuthClaims
from svc.models.garage import GarageState, GarageStatus, GarageOverview
from svc.utilities import api_utils
from svc.utilities.jwt_utils import AuthClient
from svc.utilities.rabbitmq_client import publish


def get_status(bearer_token, garage_id):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with DeviceRepository() as db:
        info = db.get_device_address_info(user_id)
        if not info:
            raise FailedDependency(description="device not registered")
        url = f'http://{info.ip_address}:{info.ip_port}'
    status = api_utils.get_garage_door_status(info.api_key, url, garage_id)
    status['doorName'] = info.node_names.get(int(garage_id))
    return GarageStatus.from_dict(status)


def get_all_status(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with DeviceRepository() as db:
        info = db.get_device_address_info(user_id)
        if not info:
            raise FailedDependency(description="device not registered")
        url = f'http://{info.ip_address}:{info.ip_port}'
    status = api_utils.get_all_garage_doors_status(info.api_key, url)
    for door in status['doors']:
        door['doorName'] = info.node_names.get(int(door['garageId']))
    return GarageOverview.from_dict(status)


def update_state(bearer_token, garage_id, request):
    AuthClient.get_instance().verify_jwt(bearer_token)
    garage_open = request.get('garageDoorOpen')
    if garage_open is None:
        raise BadRequest('Field "garageDoorOpen" is required.')
    message = {'id': garage_id, 'action': 'update', 'open': garage_open}
    publish(Automation.GARAGE.QUEUE, message)

    return GarageState(isGarageOpen=request['garageDoorOpen'])


def toggle_door(bearer_token, garage_id):
    AuthClient.get_instance().verify_jwt(bearer_token)
    message = {'id': garage_id, 'action': 'toggle'}

    publish(Automation.GARAGE.QUEUE, message)
