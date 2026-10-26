from mock import patch, ANY

from svc.controllers.registration_controller import register_garage_door, register_sump_pump, register_thermostat


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


@patch('svc.controllers.registration_controller.hvac_schedule_service')
@patch('svc.controllers.registration_controller.register_home_automation_device')
@patch('svc.controllers.registration_controller.DeviceRepository')
class TestRegisterThermostat:
    SERVICE_NAME = 'thermostat'
    IP_ADDRESS = '192.168.0.102'
    IP_PORT = 5003
    API_KEY = 'thermostat-api-key'
    DEVICE_ID = 'device-1234'
    USER_ID = 'user-1234'

    def __arrange(self, mock_db, mock_api, existing_key=None, user_id=None):
        mock_db.return_value.__enter__.return_value.get_existing_api_key.return_value = existing_key
        mock_db.return_value.__enter__.return_value.upsert_discovered_device.return_value = self.DEVICE_ID
        mock_db.return_value.__enter__.return_value.get_user_id_by_device.return_value = user_id
        mock_api.return_value = {'api_key': self.API_KEY}

    def test_register_thermostat__should_look_up_existing_key_for_thermostat_type(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api)

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_db.return_value.__enter__.return_value.get_existing_api_key.assert_called_with(self.SERVICE_NAME, 'thermostat')

    def test_register_thermostat__should_register_without_body_when_no_existing_key(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api)

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, None)

    def test_register_thermostat__should_send_existing_api_key_when_present(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api, existing_key='persisted-key')

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_api.assert_called_with(self.IP_ADDRESS, self.IP_PORT, {'api_key': 'persisted-key'})

    def test_register_thermostat__should_upsert_discovered_device_as_thermostat(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api)

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_db.return_value.__enter__.return_value.upsert_discovered_device.assert_called_with(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT, self.API_KEY, 0, [], 'thermostat')

    def test_register_thermostat__should_publish_schedule_when_device_has_owner(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api, user_id=self.USER_ID)

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_db.return_value.__enter__.return_value.get_user_id_by_device.assert_called_with(self.DEVICE_ID)
        mock_hvac.publish_hvac_schedule.assert_called_once_with(self.USER_ID)

    def test_register_thermostat__should_not_publish_schedule_when_device_unowned(self, mock_db, mock_api, mock_hvac):
        self.__arrange(mock_db, mock_api)

        register_thermostat(self.SERVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        mock_hvac.publish_hvac_schedule.assert_not_called()
