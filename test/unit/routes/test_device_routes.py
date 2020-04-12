from mock import patch

from svc.routes.device_routes import add_device_by_user_id


@patch('svc.routes.device_routes.add_device_to_role')
@patch('svc.routes.device_routes.request')
class TestDeviceRoutes:
    USER_ID = '1234abcd'
    BEARER_TOKEN = 'IMAFAKEBEARERTOKEN'

    def test_add_device_by_user__should_pass_bearer_token_to_controller(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        add_device_by_user_id(self.USER_ID)
        mock_controller.assert_called_with(self.BEARER_TOKEN, None, None)
