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
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = None
        api_key = 'test-api-key'
        nodes = [{'nodeDevice': 1, 'nodeName': 'Left'}]
        mock_api.return_value = {'api_key': api_key, 'nodes': nodes}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, api_key, self.MAX_NODES, nodes, 'garage_door')

    def test_register_garage_door__should_call_register_home_automation_device_without_body_when_no_existing_key(self, mock_db, mock_api):
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = None
        mock_api.return_value = {'api_key': 'key'}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, None)

    def test_register_garage_door__should_send_existing_api_key_in_body_when_present(self, mock_db, mock_api):
        existing_key = 'persisted-key'
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = existing_key
        mock_api.return_value = {'api_key': 'whatever'}
        register_garage_door(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, {'api_key': existing_key})


@patch('svc.controllers.registration_controller.get_host_ip')
@patch('svc.controllers.registration_controller.register_home_automation_device')
@patch('svc.controllers.registration_controller.DeviceRepository')
class TestRegisterSumpPump:
    SERVICE_NAME = 'sump-pump'
    IP_ADDRESS = '192.168.0.101'
    IP_PORT = 5001
    MAX_NODES = 1

    def test_register_sump_pump__should_upsert_with_sump_pump_type(self, mock_db, mock_api, mock_host):
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = None
        register_sump_pump(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(
            self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, ANY, self.MAX_NODES, [], 'sump_pump'
        )

    def test_register_sump_pump__should_call_register_home_automation_device(self, mock_db, mock_api, mock_host):
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = None
        mock_host.return_value = '192.168.0.1'
        register_sump_pump(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, {'api_key': ANY, 'ip_address': '192.168.0.1', 'port': 5000})

    def test_register_sump_pump__should_reuse_existing_api_key_when_present(self, mock_db, mock_api, mock_host):
        existing_key = 'persisted-sump-key'
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = existing_key
        mock_host.return_value = '192.168.0.1'
        register_sump_pump(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.MAX_NODES)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(
            self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, existing_key, self.MAX_NODES, [], 'sump_pump'
        )
        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, {'api_key': existing_key, 'ip_address': '192.168.0.1', 'port': 5000})