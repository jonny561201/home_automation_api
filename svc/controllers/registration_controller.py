from svc.db.repositories.device_repository import DeviceRepository
from svc.utilities.api_utils import register_home_automation_device


def register_garage_door(service_name, ip, port, max_nodes):
    response = register_home_automation_device(ip, port)
    api_key = response['api_key']
    nodes = response.get('nodes', [])
    with DeviceRepository() as database:
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, nodes)


def register_sump_pump(service_name, ip, port):
    response = register_home_automation_device(ip, port)
    api_key = response['api_key']

    with DeviceRepository() as database:
        database.upsert_discovered_device(service_name, ip, port, api_key)