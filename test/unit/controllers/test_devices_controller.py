import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import Devices, DeviceType
from svc.models.devices import Device
from svc.constants.home_automation import AuthClaims
from svc.controllers.devices_controller import add_device, get_user_devices, discover_device, register_discovered_device_to_user


@patch('svc.controllers.devices_controller.auth0_service')
@patch('svc.controllers.devices_controller.DeviceRepository')
@patch('svc.controllers.devices_controller.AuthClient')
class TestDeviceController:
    BEARER_TOKEN = '123abcd'
    USER_ID = '78890abvc'
    AUTH0_ID = 'auth0|fake_user'
    CLAIMS = {AuthClaims.USER_ID: USER_ID, AuthClaims.AUTH0_ID: AUTH0_ID}
    ROLE_NAME = 'test_role'
    IP_ADDRESS = '192.168.0.55'
    IP_PORT = 8080

    def test_get_user_devices__should_validate_jwt(self, mock_jwt, mock_db, mock_auth0):
        get_user_devices(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_user_devices__should_call_database_with_user_id(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_user_devices(self.BEARER_TOKEN)

        mock_db.return_value.__enter__.return_value.get_registered_devices.assert_called_with(self.USER_ID)

    def test_get_user_devices__should_map_devices_from_database(self, mock_jwt, mock_db, mock_auth0):
        device = Devices(ip_address=self.IP_ADDRESS, name='test-device', max_nodes=1, device_type=DeviceType(type='good'))
        device.nodes = []
        mock_db.return_value.__enter__.return_value.get_registered_devices.return_value = [device]

        actual = get_user_devices(self.BEARER_TOKEN)

        assert len(actual.devices) == 1
        assert actual.devices[0].name == 'test-device'

    def test_get_user_devices__should_return_empty_list_if_no_devices(self, mock_jwt, mock_db, mock_auth0):
        mock_db.return_value.__enter__.return_value.get_registered_devices.return_value = []

        actual = get_user_devices(self.BEARER_TOKEN)

        assert actual.devices == []

    def test_add_device__should_validate_jwt(self, mock_jwt, mock_db, mock_auth0):
        request_data = {'roleName': None, 'ipAddress': None, 'ipPort': None}
        add_device(self.BEARER_TOKEN, request_data)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_add_device__should_call_add_new_device_with_user_id(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        request_data = {'roleName': None, 'ipAddress': None, 'ipPort': None}
        add_device(self.BEARER_TOKEN, request_data)
        mock_db.return_value.__enter__.return_value.add_new_device.assert_called_with(self.USER_ID, ANY, ANY, ANY)

    def test_add_device__should_call_add_new_device_with_role_name(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        request_data = {'roleName': self.ROLE_NAME, 'ipAddress': None, 'ipPort': None}
        add_device(self.BEARER_TOKEN, request_data)
        mock_db.return_value.__enter__.return_value.add_new_device.assert_called_with(ANY, self.ROLE_NAME, ANY, ANY)

    def test_add_device__should_call_add_new_device_with_ip_address(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        request_data = {'roleName': None, 'ipAddress': self.IP_ADDRESS, 'ipPort': None}
        add_device(self.BEARER_TOKEN, request_data)
        mock_db.return_value.__enter__.return_value.add_new_device.assert_called_with(ANY, ANY, self.IP_ADDRESS, ANY)

    def test_add_device__should_call_add_new_device_with_ip_port(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        request_data = {'roleName': None, 'ipAddress': None, 'ipPort': self.IP_PORT}
        add_device(self.BEARER_TOKEN, request_data)
        mock_db.return_value.__enter__.return_value.add_new_device.assert_called_with(ANY, ANY, ANY, self.IP_PORT)

    def test_add_device__should_raise_bad_request_exception_if_key_missing(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        request_data = {}
        with pytest.raises(BadRequest):
            add_device(self.BEARER_TOKEN, request_data)

    def test_add_device__should_return_response_from_adding_to_database(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        device_id = 'fakeDeviceId'
        mock_db.return_value.__enter__.return_value.add_new_device.return_value = device_id
        request_data = {'roleName': 'fakeName', 'ipAddress': '1.1.1.1', 'ipPort': 443}
        actual = add_device(self.BEARER_TOKEN, request_data)

        assert actual == Device(deviceId=device_id)

    def test_add_device__should_assign_auth0_roles(self, mock_jwt, mock_db, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.return_value = ['rol_abc']
        request_data = {'roleName': 'fakeName', 'ipAddress': '1.1.1.1', 'ipPort': 443}

        add_device(self.BEARER_TOKEN, request_data)

        mock_auth0.assign_roles.assert_called_with(self.AUTH0_ID, ['rol_abc'])


@patch('svc.controllers.devices_controller.auth0_service')
@patch('svc.controllers.devices_controller.UserRepository')
@patch('svc.controllers.devices_controller.DeviceRepository')
@patch('svc.controllers.devices_controller.AuthClient')
class TestRegisterDiscoveredDevice:
    BEARER_TOKEN = '123abcd'
    USER_ID = '78890abvc'
    AUTH0_ID = 'auth0|fake_user'
    DEVICE_ID = 'device-5678'
    CLAIMS = {AuthClaims.USER_ID: USER_ID, AuthClaims.AUTH0_ID: AUTH0_ID}

    def test_register_discovered_device__should_validate_jwt(self, mock_jwt, mock_db, mock_user, mock_auth0):
        register_discovered_device_to_user(self.BEARER_TOKEN, self.DEVICE_ID, {})

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_register_discovered_device__should_call_register_device_to_user(self, mock_jwt, mock_db, mock_user, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        nodes = [{'nodeDevice': 1, 'nodeName': 'Left'}]

        register_discovered_device_to_user(self.BEARER_TOKEN, self.DEVICE_ID, {'nodes': nodes})

        mock_db.return_value.__enter__.return_value.register_device_to_user.assert_called_with(self.DEVICE_ID, self.USER_ID, nodes)

    def test_register_discovered_device__should_get_role_ids_by_device_ids(self, mock_jwt, mock_db, mock_user, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS

        register_discovered_device_to_user(self.BEARER_TOKEN, self.DEVICE_ID, {})

        mock_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.assert_called_with(self.USER_ID, [self.DEVICE_ID])

    def test_register_discovered_device__should_assign_auth0_roles(self, mock_jwt, mock_db, mock_user, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.return_value = ['rol_abc']

        register_discovered_device_to_user(self.BEARER_TOKEN, self.DEVICE_ID, {})

        mock_auth0.assign_roles.assert_called_with(self.AUTH0_ID, ['rol_abc'])

    def test_register_discovered_device__should_return_device_id(self, mock_jwt, mock_db, mock_user, mock_auth0):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.register_device_to_user.return_value = self.DEVICE_ID

        actual = register_discovered_device_to_user(self.BEARER_TOKEN, self.DEVICE_ID, {})

        assert actual == Device(deviceId=self.DEVICE_ID)
