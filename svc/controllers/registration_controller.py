import secrets

from svc.db.repositories.device_repository import DeviceRepository
from svc.utilities.api_utils import register_home_automation_device, get_host_ip


def register_garage_door(service_name: str, ip: str, port: int, max_nodes: int):
    with DeviceRepository() as database:
        existing_key = database.get_existing_api_key(service_name, 'garage_door')
        body = {'api_key': existing_key} if existing_key != None else None
        response = register_home_automation_device(ip, port, body)
        api_key = response['api_key']
        nodes = response.get('nodes', [])
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, nodes, 'garage_door')


def register_sump_pump(service_name: str, ip: str, port: int, max_nodes: int):
    with DeviceRepository() as database:
        existing_key = database.get_existing_api_key(service_name, 'sump_pump')
        api_key = existing_key if existing_key != None else secrets.token_hex(32)
        database.upsert_discovered_device(service_name, ip, port, api_key, max_nodes, [], 'sump_pump')

    request = {'api_key': api_key, 'ip_address': get_host_ip(), 'port': 5000}
    register_home_automation_device(ip, port, request)
