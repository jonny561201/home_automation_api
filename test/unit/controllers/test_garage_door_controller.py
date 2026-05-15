import os
import uuid

import jwt
import pytest
from mock import patch
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import Automation, AuthClaims
from svc.controllers.garage_door_controller import get_all_status, toggle_door, update_state, schedule_close, cancel_scheduled_close
from svc.models.app import Preference
from svc.models.devices import DeviceInfo, NodeInfo


@patch('svc.controllers.garage_door_controller.garage_status_service')
@patch('svc.controllers.garage_door_controller.UserRepository')
@patch('svc.controllers.garage_door_controller.publish')
@patch('svc.controllers.garage_door_controller.api_utils')
@patch('svc.controllers.garage_door_controller.DeviceRepository')
@patch('svc.controllers.garage_door_controller.AuthClient')
class TestGarageController:
    GARAGE_ID = '3'
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
        self.DEVICE_INFO = DeviceInfo(id='fake-device-id', ip_address=self.IP_ADDRESS, ip_port=self.IP_PORT, api_key=self.API_KEY, nodes={self.GARAGE_ID: NodeInfo(name='Left Garage', nodeId=str(uuid.uuid4()))})
        self.OVERVIEW_RESPONSE = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': []}
        self.PREFERENCE = Preference(city='Austin', tempUnit='fahrenheit', measureUnit='imperial', garageAlertTime=5)

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_update_state__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_update_state__should_call_publish(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'update', 'open': self.REQUEST['garageDoorOpen']})

    def test_update_state__should_throw_bad_request_when_field_missing(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        bad_request = {'badKey': 'fakerequest'}
        with pytest.raises(BadRequest):
            update_state(self.JWT_TOKEN, self.GARAGE_ID, bad_request)

    def test_update_state__should_return_api_response_when_success(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        actual = update_state(self.JWT_TOKEN, self.GARAGE_ID, self.REQUEST)

        assert actual.isGarageOpen == self.REQUEST['garageDoorOpen']

    def test_toggle_garage_door_state__should_validate_bearer_token(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_toggle_garage_door_state__should_call_publish(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        toggle_door(self.JWT_TOKEN, self.GARAGE_ID)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'toggle'})

    def test_get_all_status__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        mock_service.build_user_doors.return_value = []

        get_all_status(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_all_status__should_get_device_address_info(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        mock_service.build_user_doors.return_value = []

        get_all_status(self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_device_info.assert_called_with('garage_door')

    def test_get_all_status__should_call_get_all_garage_doors_status(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        mock_service.build_user_doors.return_value = []

        get_all_status(self.JWT_TOKEN)

        expected_url = f'http://{self.IP_ADDRESS}:{self.IP_PORT}'
        mock_util.get_all_garage_doors_status.assert_called_with(self.API_KEY, expected_url)

    def test_get_all_status__should_delegate_door_augmentation_to_service(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        raw_doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': True, 'duration': '2025-01-01T00:00:00'}]
        mock_util.get_all_garage_doors_status.return_value = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': raw_doors}
        mock_service.build_user_doors.return_value = []

        get_all_status(self.JWT_TOKEN)

        mock_service.build_user_doors.assert_called_with(raw_doors, self.DEVICE_INFO, self.PREFERENCE.garageAlertTime)

    def test_get_all_status__should_return_api_response_with_service_doors(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_util.get_all_garage_doors_status.return_value = self.OVERVIEW_RESPONSE
        augmented = [{'garageId': self.GARAGE_ID, 'isGarageOpen': True, 'duration': '2025-01-01T00:00:00',
                      'doorName': 'Left', 'nodeId': 'n1', 'isPastAlertTime': True, 'openTooLong': True}]
        mock_service.build_user_doors.return_value = augmented

        actual = get_all_status(self.JWT_TOKEN)

        assert actual.coordinates.latitude == 1.0
        assert actual.doors[0].openTooLong is True

    def test_cancel_scheduled_close__should_validate_jwt(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        cancel_scheduled_close(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_cancel_scheduled_close__should_call_cancel_garage_schedule(self, mock_jwt, mock_db, mock_util, mock_publish, mock_user, mock_service):
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        cancel_scheduled_close(self.JWT_TOKEN, self.GARAGE_ID)

        expected_url = f'http://{self.IP_ADDRESS}:{self.IP_PORT}'
        mock_util.cancel_garage_schedule.assert_called_with(self.API_KEY, expected_url, self.GARAGE_ID)


@patch('svc.controllers.garage_door_controller.publish')
@patch('svc.controllers.garage_door_controller.UserRepository')
@patch('svc.controllers.garage_door_controller.AuthClient')
class TestScheduleClose:
    GARAGE_ID = '3'
    USER_ID = 'fakeUserId'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    JWT_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')

    def setup_method(self):
        self.PREFERENCE = Preference(city='Austin', tempUnit='fahrenheit', measureUnit='imperial', garageAlertTime=5)

    def test_schedule_close__should_validate_jwt(self, mock_jwt, mock_user, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        schedule_close(self.JWT_TOKEN, self.GARAGE_ID)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_schedule_close__should_get_preferences_by_user(self, mock_jwt, mock_user, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        schedule_close(self.JWT_TOKEN, self.GARAGE_ID)

        mock_user.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_schedule_close__should_publish_with_delay_in_seconds(self, mock_jwt, mock_user, mock_publish):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        schedule_close(self.JWT_TOKEN, self.GARAGE_ID)

        mock_publish.assert_called_with(Automation.GARAGE.QUEUE, {'id': self.GARAGE_ID, 'action': 'schedule', 'delay_seconds': 300})
