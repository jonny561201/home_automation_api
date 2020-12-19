import os

import jwt
from mock import patch

from svc.controllers.garage_door_controller import get_status, toggle_door, update_state


@patch('svc.controllers.garage_door_controller.api_utils')
@patch('svc.controllers.garage_door_controller.get_garage_url_by_user')
@patch('svc.controllers.garage_door_controller.is_jwt_valid')
class TestGarageController:
    GARAGE_ID = 3
    USER_ID = 'fakeUserId'
    JWT_SECRET = 'fake_jwt_secret'
    SUCCESS_STATE = 200
    FAILURE_STATUS = 500
    JWT_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256').decode('UTF-8')

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_get_status__should_call_is_jwt_valid(self, mock_jwt, mock_url, mock_util):
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        get_status(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_status__should_get_garage_url_by_user(self, mock_jwt, mock_url, mock_util):
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        get_status(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_url.assert_called_with(self.USER_ID)

    def test_get_status__should_call_get_garage_door_status(self, mock_jwt, mock_url, mock_util):
        expected_url = 'http://www.fakeurl.com/test/location'
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        mock_url.return_value = expected_url
        get_status(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_util.get_garage_door_status.assert_called_with(self.JWT_TOKEN, expected_url, self.GARAGE_ID)

    def test_get_status__should_return_api_response_for_success(self, mock_jwt, mock_url, mock_util):
        response = {'fake': 'data'}
        mock_util.get_garage_door_status.return_value = response
        actual = get_status(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        assert actual == response

    def test_update_state__should_call_is_jwt_valid(self, mock_jwt, mock_url, mock_util):
        request = {}
        mock_util.update_garage_door_state.return_value = (self.SUCCESS_STATE, {})
        update_state(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID, request)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_update_state__should_get_garage_url_by_user(self, mock_jwt, mock_url, mock_util):
        request = {}
        mock_util.update_garage_door_state.return_value = (self.SUCCESS_STATE, {})
        update_state(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID, request)

        mock_url.assert_called_with(self.USER_ID)

    def test_update_state__should_call_update_garage_door_state(self, mock_jwt, mock_url, mock_util):
        request = {}
        expected_url = 'http://www.fakeurl.com/test/location'
        mock_util.update_garage_door_state.return_value = (self.SUCCESS_STATE, {})
        mock_url.return_value = expected_url
        update_state(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID, request)

        mock_util.update_garage_door_state.assert_called_with(self.JWT_TOKEN, expected_url, self.GARAGE_ID, request)

    def test_update_state__should_return_api_response_when_success(self, mock_jwt, mock_url, mock_util):
        request = {}
        expected_url = 'http://www.fakeurl.com/test/location'
        response = {'testResponse': 'notRealData'}
        mock_url.return_value = expected_url
        mock_util.update_garage_door_state.return_value = response
        actual = update_state(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID, request)

        assert actual == response

    def test_toggle_garage_door_state__should_validate_bearer_token(self, mock_jwt, mock_url, mock_util):
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        toggle_door(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_toggle_garage_door_state__should_get_garage_url_by_user(self, mock_jwt, mock_url, mock_util):
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        toggle_door(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_url.assert_called_with(self.USER_ID)

    def test_toggle_garage_door_state__should_call_toggle_garage_door_state(self, mock_jwt, mock_url, mock_util):
        expected_url = 'http://www.fakeurl.com/test/location'
        mock_url.return_value = expected_url
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        toggle_door(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        mock_util.toggle_garage_door_state.assert_called_with(self.JWT_TOKEN, expected_url, self.GARAGE_ID)

    def test_toggle_garage_door_state__should_return_api_response_if_success(self, mock_jwt, mock_url, mock_util):
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        actual = toggle_door(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

        assert actual == self.SUCCESS_STATE
