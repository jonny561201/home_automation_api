from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import Devices
from svc.constants.home_automation import AuthClaims
from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.user_repository import UserRepository
from svc.models.devices import Device, UserDevices, UserDevice, DeviceNodeDetail
from svc.utilities.auth_utils import AuthClient
from svc.utilities import api_utils
from svc.utilities.api_utils import register_home_automation_device


# TODO: break contract and stop calling it roleName and just name
def add_device(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    auth0_id = claims[AuthClaims.AUTH0_ID]
    with DeviceRepository() as database:
        try:
            device_id = database.add_new_device(user_id, request_data['roleName'], request_data['ipAddress'], request_data['ipPort'])
            role_ids = database.get_role_ids_by_device_ids(user_id, [device_id])
        except KeyError:
            raise BadRequest
    if role_ids:
        api_utils.assign_auth0_roles(auth0_id, role_ids)
    return Device(deviceId=device_id)


def get_user_devices(bearer_token):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    with DeviceRepository() as database:
        is_child = database.is_child_user(user_id)
        devices = database.get_registered_devices(user_id) if is_child else database.get_all_devices()
        user_devices = [_create_user_device(device) for device in devices]
        return UserDevices(devices=user_devices)


def register_discovered_device_to_user(bearer_token, device_id, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    auth0_id = claims[AuthClaims.AUTH0_ID]
    nodes = request_data.get('nodes', [])
    with DeviceRepository() as database:
        registered_id = database.register_device_to_user(device_id, user_id, nodes)
        role_ids = database.get_role_ids_by_device_ids(user_id, [device_id])
    if role_ids:
        api_utils.assign_auth0_roles(auth0_id, role_ids)
    preferred = next((n for n in nodes if n.get('preferred')), None)
    if preferred:
        with DeviceRepository() as database:
            preferred_node_id = database.get_node_id_by_device(device_id, preferred['nodeDevice'])
        with UserRepository() as database:
            database.insert_preferences_by_user(user_id, {'preferredGarageNodeId': preferred_node_id})
    return Device(deviceId=registered_id)


def discover_device(service_name, ip, port, max_nodes, device_type_name):
    response = register_home_automation_device(ip, port)
    api_key = response['api_key']
    nodes = response.get('nodes', [])
    with DeviceRepository() as database:
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, nodes, device_type_name)


def _create_user_device(device: Devices):
    nodes = [DeviceNodeDetail(nodeDevice=n.node_device, nodeName=n.node_name) for n in device.nodes]
    return UserDevice(deviceId=str(device.id), registered=device.registered, type=device.device_type.type,
                      name=device.name, maxNodes=device.max_nodes, nodes=nodes)
