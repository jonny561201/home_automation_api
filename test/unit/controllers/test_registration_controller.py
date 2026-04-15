from mock import patch

from svc.controllers.registration_controller import register_garage_door


@patch('svc.controllers.registration_controller.register_home_automation_device')
@patch('svc.controllers.registration_controller.DeviceRepository')
class TestRegisterDevice:
    SERVICE_NAME = 'garage_opener'
    IP_ADDRESS = '192.168.0.100'
    IP_PORT = 5000
    MAX_NODES = 2

    def test_register_device__should_upsert_discovered_device(self, mock_db, mock_api):
        api_key = 'test-api-key'
        nodes = [{'nodeDevice': 1, 'nodeName': 'Left'}]
        mock_api.return_value = {'api_key': api_key, 'nodes': nodes}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, api_key, self.MAX_NODES, nodes)

    def test_register_device__should_call_register_garage_device(self, mock_db, mock_api):
        mock_api.return_value = {'api_key': 'key'}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT)