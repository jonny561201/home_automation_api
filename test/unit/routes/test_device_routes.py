import json

from mock import patch, ANY

from svc.routes.device_routes import add_device_by_user_id, add_device_node_by_user_id


@patch('svc.routes.device_routes.devices_controller')
@patch('svc.routes.device_routes.request')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'
    DEVICE_ID = '890xyz'

    def test_add_device_by_user_id__should_pass_bearer_token_to_controller(self, mock_request, mock_controller):
        mock_controller.add_device_to_role.return_value = {}
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        mock_request.data = json.dumps({}).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.add_device_to_role.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_add_device_by_user_id__should_pass_user_id_to_controller(self, mock_request, mock_controller):
        mock_controller.add_device_to_role.return_value = {}
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.add_device_to_role.assert_called_with(ANY, self.USER_ID, ANY)

    def test_add_device_by_user_id__should_pass_the_decoded_request_body_to_controller(self, mock_request, mock_controller):
        mock_controller.add_device_to_role.return_value = {}
        request_data = {'fakeData': 'Im Not Real'}
        mock_request.data = json.dumps(request_data).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.add_device_to_role.assert_called_with(ANY, ANY, request_data)

    def test_add_device_by_user_id__should_return_status_code_200(self, mock_request, mock_controller):
        mock_controller.add_device_to_role.return_value = {}
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        actual = add_device_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_add_device_by_user_id__should_return_default_headers(self, mock_request, mock_controller):
        mock_controller.add_device_to_role.return_value = {}
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        actual = add_device_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_add_device_by_user_id__should_return_device_id(self, mock_request, mock_controller):
        device_id = 'fake_device_id'
        mock_controller.add_device_to_role.return_value = device_id
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        actual = add_device_by_user_id(self.USER_ID)

        assert json.loads(actual.data.decode('UTF-8'))['deviceId'] == device_id

    def test_add_device_node_by_user_id__should_pass_bearer_token_to_controller(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        mock_request.data = json.dumps({}).encode()
        add_device_node_by_user_id(self.USER_ID, self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_add_device_node_by_user_id__should_pass_the_decoded_body_to_the_controller(self, mock_request, mock_controller):
        request_data = {'test': 'test'}
        mock_request.data = json.dumps(request_data).encode('UTF-8')
        add_device_node_by_user_id(self.USER_ID, self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(ANY, ANY, request_data)

    def test_add_device_node_by_user_id__should_pass_the_device_id_to_the_controller(self, mock_request, mock_controller):
        request_data = {'test': 'test'}
        mock_request.data = json.dumps(request_data).encode('UTF-8')
        add_device_node_by_user_id(self.USER_ID, self.DEVICE_ID)

        mock_controller.add_node_to_device.assert_called_with(ANY, self.DEVICE_ID, ANY)

    def test_add_device_node_by_user_id__should_return_success_status_code(self, mock_request, mock_controller):
        mock_request.data = json.dumps({}).encode()
        actual = add_device_node_by_user_id(self.USER_ID, self.DEVICE_ID)

        assert actual.status_code == 200

    def test_add_device_node_by_user_id__should_return_default_headers(self, mock_request, mock_controller):
        mock_request.data = json.dumps({}).encode()
        actual = add_device_node_by_user_id(self.USER_ID, self.DEVICE_ID)

        assert actual.content_type == 'text/json'
