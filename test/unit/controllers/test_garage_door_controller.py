import os

import jwt
import pytest
from mock import patch
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import Automation, AuthClaims
from svc.controllers.garage_door_controller import get_all_status, get_status, toggle_door, update_state
from svc.models.devices import DeviceInfo


@patch('svc.controllers.garage_door_controller.publish')
@patch('svc.controllers.garage_door_controller.api_utils')
@patch('svc.controllers.garage_door_controller.DeviceRepository')
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
    IP_ADDRESS = '1.1.1.1'
    IP_PORT = 5000
    API_KEY = 'fake-api-key'

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})
        self.DEVICE_INFO = DeviceInfo(ip_address=self.IP_ADDRESS, ip_port=self.IP_PORT, api_key=self.API_KEY, node_names={self.GARAGE_ID: 'Left Garage'})
        self.STATUS_RESPONSE = {'isGarageOpen': True, 'duration': '2025-01-01T00:00:00', 'coordinates': {'latitude': 1.0, 'longitude': 2.0}}
        self.OVERVIEW_RESPONSE = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': []}

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_get_status__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_garage_door_status.return_value = self.STATUS_RESPONSE
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_status__should_get_device_address_info_by_user(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_garage_door_status.return_value = self.STATUS_RESPONSE
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        mock_db.return_value.__enter__.return_value.get_device_address_info.assert_called_with(self.USER_ID)

    def test_get_status__should_call_get_garage_door_status(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_garage_door_status.return_value = self.STATUS_RESPONSE
        get_status(self.JWT_TOKEN, self.GARAGE_ID)

        expected_url = f'http://{self.IP_ADDRESS}:{self.IP_PORT}'
        mock_util.get_garage_door_status.assert_called_with(self.API_KEY, expected_url, self.GARAGE_ID)

    def test_get_status__should_return_garage_status(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_garage_door_status.return_value = dict(self.STATUS_RESPONSE)
        actual = get_status(self.JWT_TOKEN, self.GARAGE_ID)

        assert actual.doorName == 'Left Garage'

    def test_update_state__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_util, mock_publish):
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_update_state__should_call_publish(self, mock_jwt, mock_db, mock_util, mock_publish):
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'update', 'open': self.REQUEST['garageDoorOpen']})

    def test_update_state__should_throw_bad_request_when_field_missing(self, mock_jwt, mock_db, mock_util, mock_publish):
        bad_request = {'badKey': 'fakerequest'}
        with pytest.raises(BadRequest):
            update_state(self.JWT_TOKEN, self.GARAGE_ID, bad_request)

    def test_update_state__should_return_api_response_when_success(self, mock_jwt, mock_db, mock_util, mock_publish):
        actual = update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        assert actual.isGarageOpen == self.REQUEST['garageDoorOpen']

    def test_toggle_garage_door_state__should_validate_bearer_token(self, mock_jwt, mock_db, mock_util, mock_publish):
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_toggle_garage_door_state__should_call_publish(self, mock_jwt, mock_db, mock_util, mock_publish):
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'toggle'})

    def test_get_all_status__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        get_all_status(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_all_status__should_get_device_address_info_by_user(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        get_all_status(self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_device_address_info.assert_called_with(self.USER_ID)

    def test_get_all_status__should_call_get_all_garage_doors_status(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        get_all_status(self.JWT_TOKEN)

        expected_url = f'http://{self.IP_ADDRESS}:{self.IP_PORT}'
        mock_util.get_all_garage_doors_status.assert_called_with(self.API_KEY, expected_url)

    def test_get_all_status__should_return_api_response(self, mock_jwt, mock_db, mock_util, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_address_info.return_value = self.DEVICE_INFO
        response = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': []}
        mock_util.get_all_garage_doors_status.return_value = response
        actual = get_all_status(self.JWT_TOKEN)

        assert actual.coordinates.latitude == 1.0

