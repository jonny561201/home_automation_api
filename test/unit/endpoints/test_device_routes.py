from flask import Flask
from mock import patch, ANY

from svc.endpoints.device_routes import add_device, get_devices
from svc.models.devices import Device, UserDevice, UserDevices
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.device_routes.devices_controller')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'
    HEADERS = {'Authorization': BEARER_TOKEN}
    DEVICE_ID = '890xyz'
    IP_ADDRESS = '192.168.0.1'

    def setup_method(self):
        self.app = Flask(__name__)
        self.DEVICE_ID = Device(deviceId=self.DEVICE_ID)
        self.DEVICE = UserDevice(deviceId='device-1', name='test', type='garage', registered=True)
        self.ctx = setup_request(self.app, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_add_device__should_pass_bearer_token_to_controller(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE_ID
        add_device()
        mock_controller.add_device.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_add_device__should_pass_the_decoded_request_body_to_controller(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE_ID
        request_data = {'fakeData': 'Im Not Real'}
        self.ctx = setup_request(self.app, self.ctx, request_data, self.HEADERS)
        add_device()
        mock_controller.add_device.assert_called_with(ANY, request_data)

    def test_add_device__should_return_status_code_200(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE_ID
        actual = add_device()

        assert actual.status_code == 200

    def test_add_device__should_return_default_headers(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE_ID
        actual = add_device()

        assert actual.content_type == 'application/json'

    def test_add_device__should_return_device_id(self, mock_controller):
        device_id = 'fake_device_id'
        mock_controller.add_device.return_value = Device(deviceId=device_id)
        actual = add_device()

        assert actual.json['deviceId'] == device_id

    def test_get_devices__should_pass_bearer_token_to_controller(self, mock_controller):
        get_devices()

        mock_controller.get_user_devices.assert_called_with(self.BEARER_TOKEN)

    def test_get_devices__should_return_status_code_200(self, mock_controller):
        actual = get_devices()

        assert actual.status_code == 200

    def test_get_devices__should_return_default_headers(self, mock_controller):
        actual = get_devices()

        assert actual.content_type == 'application/json'

    def test_get_devices__should_return_devices_from_controller(self, mock_controller):
        mock_controller.get_user_devices.return_value = UserDevices(devices=[self.DEVICE])

        actual = get_devices()

        assert actual.json == {'devices': [
            {'deviceId': self.DEVICE.deviceId, 'name': self.DEVICE.name,
             'type': self.DEVICE.type, 'registered': self.DEVICE.registered, 'maxNodes': 1, 'nodes': []}]}
