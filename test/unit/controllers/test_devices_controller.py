from mock import patch

from svc.controllers.devices_controller import add_device_to_role


@patch('svc.controllers.devices_controller.is_jwt_valid')
class TestDeviceController:
    BEARER_TOKEN = '123abcd'

    def test_add_device_to_role__should_validate_jwt(self, mock_jwt):
        request_data = {}
        add_device_to_role(self.BEARER_TOKEN, request_data)
        mock_jwt.assert_called_with(self.BEARER_TOKEN)
