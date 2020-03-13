import os

import jwt
from mock import patch

from svc.controllers.garage_door_controller import get_status, toggle_door, update_state


@patch('svc.controllers.garage_door_controller.get_garage_url_by_user')
@patch('svc.controllers.garage_door_controller.is_jwt_valid')
class TestGarageController:
    USER_ID = 'fakeUserId'
    JWT_SECRET = 'fake_jwt_secret'
    JWT_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256').decode('UTF-8')

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_garage_door_status__should_call_is_jwt_valid(self, mock_jwt, mock_url):
        get_status(self.JWT_TOKEN, self.USER_ID)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_garage_door_status__should_get_garage_url_by_user(self, mock_jwt, mock_url):
        get_status(self.JWT_TOKEN, self.USER_ID)

        mock_url.assert_called_with(self.USER_ID)

    def test_update_state__should_call_is_jwt_valid(self, mock_jwt, mock_url):
        request = {}
        update_state(self.JWT_TOKEN, self.USER_ID, request)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_update_state__should_get_garage_url_by_user(self, mock_jwt, mock_ur):
        request = {}
        update_state(self.JWT_TOKEN, self.USER_ID, request)

        mock_ur.assert_called_with(self.USER_ID)

    def test_toggle_garage_door_state__should_validate_bearer_token(self, mock_jwt, mock_url):
        toggle_door(self.JWT_TOKEN, self.USER_ID)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_toggle_garage_door_state__should_get_garage_url_by_user(self, mock_jwt, mock_url):
        toggle_door(self.JWT_TOKEN, self.USER_ID)

        mock_url.assert_called_with(self.USER_ID)