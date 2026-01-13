from werkzeug.exceptions import BadRequest

from svc.db.methods.device_repository import DeviceRepository
from svc.models.device import Device
from svc.utilities.jwt_utils import is_jwt_valid


def add_device_to_role(bearer_token, user_id, request_data):
    is_jwt_valid(bearer_token)
    with DeviceRepository() as database:
        try:
            device_id = database.add_new_role_device(user_id, request_data['roleName'], request_data['ipAddress'])
            return Device(deviceId=device_id)
        except KeyError:
            raise BadRequest


def add_node_to_device(bearer_token, user_id, device_id, request_data):
    is_jwt_valid(bearer_token)
    with DeviceRepository() as database:
        try:
            return database.add_new_device_node(user_id, device_id, request_data['nodeName'], request_data.get('preferred'))
        except KeyError:
            raise BadRequest
