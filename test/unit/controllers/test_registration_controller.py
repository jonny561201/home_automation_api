from mock import patch, ANY

from svc.controllers.registration_controller import register_garage_door, register_sump_pump


@patch('svc.controllers.registration_controller.register_home_automation_device')
@patch('svc.controllers.registration_controller.DeviceRepository')
class TestRegisterGarageDoor:
    SERVICE_NAME = 'garage_opener'
    IP_ADDRESS = '192.168.0.100'
    IP_PORT = 5000
    MAX_NODES = 2

    def test_register_garage_door__should_upsert_discovered_device(self, mock_db, mock_api):
        api_key = 'test-api-key'
        nodes = [{'nodeDevice': 1, 'nodeName': 'Left'}]
        mock_api.return_value = {'api_key': api_key, 'nodes': nodes}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, api_key, self.MAX_NODES, nodes, 'garage_door')

    def test_register_garage_door__should_call_register_home_automation_device(self, mock_db, mock_api):
        mock_api.return_value = {'api_key': 'key'}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT)


@patch('svc.controllers.registration_controller.get_host_ip')
@patch('svc.controllers.registration_controller.register_home_automation_device')
@patch('svc.controllers.registration_controller.DeviceRepository')
class TestRegisterSumpPump:
    SERVICE_NAME = 'sump-pump'
    IP_ADDRESS = '192.168.0.101'
    IP_PORT = 5001
    MAX_NODES = 1

    def test_register_sump_pump__should_upsert_with_sump_pump_type(self, mock_db, mock_api, mock_host):
        register_sump_pump(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(
            self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, ANY, self.MAX_NODES, [], 'sump_pump'
        )

    def test_register_sump_pump__should_call_register_home_automation_device(self, mock_db, mock_api, mock_host):
        mock_host.return_value = '192.168.0.1'
        register_sump_pump(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, {'api_key': ANY, 'ip_address': '192.168.0.1', 'port': 5000})