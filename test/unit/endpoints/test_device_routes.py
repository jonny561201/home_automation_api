import json

from flask import Flask, request
from mock import patch, ANY

from svc.models.device import DeviceNode, DoorDeviceDetails
from svc.models.device import Device
from svc.endpoints.device_routes import add_device, add_device_node


@patch('svc.endpoints.device_routes.devices_controller')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'
    DEVICE_ID = '890xyz'

    def setup_method(self):
        self.app = Flask(__name__)
        self.DEVICE = Device(deviceId=self.DEVICE_ID)
        self.NODE = DeviceNode(availableNodes=1, device=DoorDeviceDetails(doorId=1, doorName='Test Door'))
        self.ctx = self.app.test_request_context(data=json.dumps({}), headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_add_device__should_pass_bearer_token_to_controller(self, mock_controller):
        mock_controller.add_device_to_role.return_value = self.DEVICE
        add_device()
        mock_controller.add_device_to_role.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_add_device__should_pass_the_decoded_request_body_to_controller(self, mock_controller):
        mock_controller.add_device_to_role.return_value = self.DEVICE
        request_data = {'fakeData': 'Im Not Real'}
        request.data = json.dumps(request_data).encode('UTF-8')
        add_device()
        mock_controller.add_device_to_role.assert_called_with(ANY, request_data)

    def test_add_device__should_return_status_code_200(self, mock_controller):
        mock_controller.add_device_to_role.return_value = self.DEVICE
        actual = add_device()

        assert actual.status_code == 200

    def test_add_device__should_return_default_headers(self, mock_controller):
        mock_controller.add_device_to_role.return_value = self.DEVICE
        actual = add_device()

        assert actual.content_type == 'application/json'

    def test_add_device__should_return_device_id(self, mock_controller):
        device_id = 'fake_device_id'
        mock_controller.add_device_to_role.return_value = Device(deviceId=device_id)
        actual = add_device()

        assert json.loads(actual.data.decode('UTF-8'))['deviceId'] == device_id

    def test_add_device_node__should_pass_bearer_token_to_controller(self, mock_controller):
        mock_controller.add_node_to_device.return_value = self.NODE
        add_device_node(self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_add_device_node__should_pass_the_decoded_body_to_the_controller(self, mock_controller):
        request_data = {'test': 'test'}
        mock_controller.add_node_to_device.return_value = self.NODE
        request.data = json.dumps(request_data).encode('UTF-8')
        add_device_node(self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(ANY, ANY, request_data)

    def test_add_device_node__should_pass_the_device_id_to_the_controller(self, mock_controller):
        mock_controller.add_node_to_device.return_value = self.NODE
        add_device_node(self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(ANY, self.DEVICE_ID, ANY)

    def test_add_device_node__should_return_success_status_code(self, mock_controller):
        mock_controller.add_node_to_device.return_value = self.NODE
        actual = add_device_node(self.DEVICE_ID)

        assert actual.status_code == 200

    def test_add_device_node__should_return_default_headers(self, mock_controller):
        mock_controller.add_node_to_device.return_value = self.NODE
        actual = add_device_node(self.DEVICE_ID)

        assert actual.content_type == 'application/json'

    def test_add_device_node__should_return_controller_response(self, mock_controller):
        mock_controller.add_node_to_device.return_value = self.NODE
        actual = add_device_node(self.DEVICE_ID)

        assert actual.data.decode('UTF-8') == self.NODE.to_json()
