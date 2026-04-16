import secrets

from svc.db.repositories.device_repository import DeviceRepository
from svc.utilities.api_utils import register_home_automation_device, get_host_ip


def register_garage_door(service_name: str, ip: str, port: int, max_nodes: int):
    response = register_home_automation_device(ip, port)
    api_key = response['api_key']
    nodes = response.get('nodes', [])
    with DeviceRepository() as database:
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, nodes)


def register_sump_pump(service_name: str, ip: str, port: int, max_nodes: int):
    api_key = secrets.token_hex(32)
    with DeviceRepository() as database:
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, [])

    request = {'api_key': api_key, 'ip_address': get_host_ip(), 'port': 5000}
    register_home_automation_device(ip, port, request)
