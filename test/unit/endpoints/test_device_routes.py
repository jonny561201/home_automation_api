import json

from flask import Flask
from mock import patch, ANY

from svc.models.device import DeviceNode, DoorDeviceDetails
from svc.models.device import Device
from svc.endpoints.device_routes import add_device
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.device_routes.devices_controller')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'
    HEADERS = {'Authorization': BEARER_TOKEN}
    DEVICE_ID = '890xyz'

    def setup_method(self):
        self.app = Flask(__name__)
        self.DEVICE = Device(deviceId=self.DEVICE_ID)
        self.NODE = DeviceNode(availableNodes=1, device=DoorDeviceDetails(doorId=1, doorName='Test Door'))
        self.ctx = setup_request(self.app, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_add_device__should_pass_bearer_token_to_controller(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE
        add_device()
        mock_controller.add_device.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_add_device__should_pass_the_decoded_request_body_to_controller(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE
        request_data = {'fakeData': 'Im Not Real'}
        self.ctx = setup_request(self.app, self.ctx, request_data, self.HEADERS)
        add_device()
        mock_controller.add_device.assert_called_with(ANY, request_data)

    def test_add_device__should_return_status_code_200(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE
        actual = add_device()

        assert actual.status_code == 200

    def test_add_device__should_return_default_headers(self, mock_controller):
        mock_controller.add_device.return_value = self.DEVICE
        actual = add_device()

        assert actual.content_type == 'application/json'

    def test_add_device__should_return_device_id(self, mock_controller):
        device_id = 'fake_device_id'
        mock_controller.add_device.return_value = Device(deviceId=device_id)
        actual = add_device()

        assert json.loads(actual.data.decode('UTF-8'))['deviceId'] == device_id
