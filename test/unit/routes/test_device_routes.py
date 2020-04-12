import json

from mock import patch, ANY

from svc.routes.device_routes import add_device_by_user_id


@patch('svc.routes.device_routes.add_device_to_role')
@patch('svc.routes.device_routes.request')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'

    def test_add_device_by_user__should_pass_bearer_token_to_controller(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        mock_request.data = json.dumps({}).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_add_device_by_user__should_pass_user_id_to_controller(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.assert_called_with(ANY, self.USER_ID, ANY)

    def test_add_device_by_user__should_pass_the_decoded_request_body_to_controller(self, mock_request, mock_controller):
        request_data = {'fakeData': 'Im Not Real'}
        mock_request.data = json.dumps(request_data).encode('UTF-8')
        add_device_by_user_id(self.USER_ID)
        mock_controller.assert_called_with(ANY, ANY, request_data)

    def test_add_device_by_user__should_return_status_code_200(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': None}
        mock_request.data = json.dumps({}).encode('UTF-8')
        actual = add_device_by_user_id(self.USER_ID)

        assert actual.status_code == 200
