from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import Devices
from svc.constants.home_automation import AuthClaims
from svc.db.repositories.device_repository import DeviceRepository
from svc.models.devices import Device, UserDevices, UserDevice
from svc.utilities.jwt_utils import AuthClient


# TODO: break contract and stop calling it roleName and just name
def add_device(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with DeviceRepository() as database:
        try:
            device_id = database.add_new_device(user_id, request_data['roleName'], request_data['ipAddress'])
            return Device(deviceId=device_id)
        except KeyError:
            raise BadRequest


def get_user_devices(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with DeviceRepository() as database:
        devices = database.get_registered_devices(user_id)
        user_devices = [create_user_device(device) for device in devices]
        return UserDevices(devices=user_devices)


def create_user_device(device: Devices):
    return UserDevice(id=device.node_device, ipAddress=device.ip_address, ipPort=device.ip_port,
                      registered=device.registered, type=device.device_type.type, name=device.node_name)