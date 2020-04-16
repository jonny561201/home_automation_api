import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.controllers.devices_controller import add_device_to_role, add_node_to_device


@patch('svc.controllers.devices_controller.UserDatabaseManager')
@patch('svc.controllers.devices_controller.is_jwt_valid')
class TestDeviceController:
    BEARER_TOKEN = '123abcd'
    USER_ID = '78890abvc'
    ROLE_NAME = 'test_role'
    IP_ADDRESS = '192.168.0.55'

    def test_add_device_to_role__should_validate_jwt(self, mock_jwt, mock_db):
        request_data = {'roleName': None, 'ipAddress': None}
        add_device_to_role(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_add_device_to_role__should_call_add_new_role_with_user_id(self, mock_jwt, mock_db):
        request_data = {'roleName': None, 'ipAddress': None}
        add_device_to_role(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_db.return_value.__enter__.return_value.add_new_role_device.assert_called_with(self.USER_ID, ANY, ANY)

    def test_add_device_to_role__should_call_add_new_role_with_role_name(self, mock_jwt, mock_db):
        request_data = {'roleName': self.ROLE_NAME, 'ipAddress': None}
        add_device_to_role(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_db.return_value.__enter__.return_value.add_new_role_device.assert_called_with(ANY, self.ROLE_NAME, ANY)

    def test_add_device_to_role__should_call_add_new_role_with_ip_address(self, mock_jwt, mock_db):
        request_data = {'roleName': None, 'ipAddress': self.IP_ADDRESS}
        add_device_to_role(self.BEARER_TOKEN, self.USER_ID, request_data)
        mock_db.return_value.__enter__.return_value.add_new_role_device.assert_called_with(ANY, ANY, self.IP_ADDRESS)

    def test_add_device_to_role__should_raise_bad_request_exception_if_key_missing(self, mock_jwt, mock_db):
        request_data = {}
        with pytest.raises(BadRequest):
            add_device_to_role(self.BEARER_TOKEN, self.USER_ID, request_data)

    def test_add_node_to_device__should_call_is_jwt_valid(self, mock_jwt, mock_db):
        request_data = {'deviceId': 'fake', 'nodeName': 'fake'}
        add_node_to_device(self.BEARER_TOKEN, request_data)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_add_node_to_device__should_call_database_to_add_new_node(self, mock_jwt, mock_db):
        device_id = '657asdf'
        node_name = 'im a node name'
        request_data = {'deviceId': device_id, 'nodeName': node_name}
        add_node_to_device(self.BEARER_TOKEN, request_data)

        mock_db.return_value.__enter__.return_value.add_new_device_node.assert_called_with(device_id, node_name)
