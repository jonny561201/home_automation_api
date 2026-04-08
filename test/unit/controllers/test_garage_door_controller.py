import os

import jwt
import pytest
from mock import patch
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import Automation, AuthClaims
from svc.controllers.garage_door_controller import get_all_status, get_status, toggle_door, update_state


@patch('svc.controllers.garage_door_controller.publish')
@patch('svc.controllers.garage_door_controller.api_utils')
@patch('svc.controllers.garage_door_controller.get_garage_url_by_user')
@patch('svc.controllers.garage_door_controller.AuthClient')
class TestGarageController:
    GARAGE_ID = 3
    USER_ID = 'fakeUserId'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    JWT_SECRET = 'fake_jwt_secret'
    SUCCESS_STATE = 200
    FAILURE_STATUS = 500
    JWT_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256')
    REQUEST = {'garageDoorOpen': True}

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_get_status__should_call_is_jwt_valid(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_status__should_get_garage_url_by_user(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        mock_url.assert_called_with(self.USER_ID)

    def test_get_status__should_call_get_garage_door_status(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        expected_url = 'http://www.fakeurl.com/test/location'
        mock_util.get_garage_door_status.return_value = (self.SUCCESS_STATE, {})
        mock_url.return_value = expected_url
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        mock_util.get_garage_door_status.assert_called_with(self.JWT_TOKEN, expected_url, self.GARAGE_ID)

    def test_get_status__should_return_api_response_for_success(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        response = {'fake': 'data'}
        mock_util.get_garage_door_status.return_value = response
        actual = get_status(self.JWT_TOKEN, self.GARAGE_ID)

        assert actual == response

    def test_update_state__should_call_is_jwt_valid(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_util.update_garage_door_state.return_value = (self.SUCCESS_STATE, {})
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_update_state__should_call_publish(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_util.update_garage_door_state.return_value = (self.SUCCESS_STATE, {})
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'update', 'open': self.REQUEST['garageDoorOpen']})

    def test_update_state__should_throw_bad_request_when_field_missing(self, mock_jwt, mock_url, mock_util, mock_publish):
        bad_request = {'badKey': 'fakerequest'}
        with pytest.raises(BadRequest):
            update_state(self.JWT_TOKEN, self.GARAGE_ID, bad_request)

    def test_update_state__should_return_api_response_when_success(self, mock_jwt, mock_url, mock_util, mock_publish):
        actual = update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        assert actual.isGarageOpen == self.REQUEST['garageDoorOpen']

    def test_toggle_garage_door_state__should_validate_bearer_token(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_toggle_garage_door_state__should_call_publish(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_util.toggle_garage_door_state.return_value = self.SUCCESS_STATE
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'toggle'})

    def test_get_all_status__should_call_is_jwt_valid(self, mock_jwt, mock_url, mock_util, mock_publish):
        get_all_status(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_all_status__should_get_garage_url_by_user(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_all_status(self.JWT_TOKEN)

        mock_url.assert_called_with(self.USER_ID)

    def test_get_all_status__should_call_get_all_garage_doors_status(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        expected_url = 'http://www.fakeurl.com/test/location'
        mock_url.return_value = expected_url
        get_all_status(self.JWT_TOKEN)

        mock_util.get_all_garage_doors_status.assert_called_with(self.JWT_TOKEN, expected_url)

    def test_get_all_status__should_return_api_response(self, mock_jwt, mock_url, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        response = {'fake': 'data'}
        mock_util.get_all_garage_doors_status.return_value = response
        actual = get_all_status(self.JWT_TOKEN)

        assert actual == response

