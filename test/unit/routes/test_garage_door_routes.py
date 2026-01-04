import os
import uuid
from datetime import datetime

import jwt
from flask import json
from mock import patch

from models.garage import GarageStatus, Coordinates
from svc.endpoints.garage_door_routes import get_garage_door_status, update_garage_door_state, toggle_garage_door


@patch('svc.endpoints.garage_door_routes.garage_door_controller')
@patch('svc.endpoints.garage_door_routes.request')
class TestAppRoutes:
    GARAGE_ID = 3
    COORDINATES = Coordinates(latitude=19.00, longitude=-99.00)
    STATUS = GarageStatus(isGarageOpen=True, statusDuration=datetime.now(), coordinates=COORDINATES)
    USER_ID = str(uuid.uuid4())
    JWT_SECRET = 'fake_jwt_secret'
    JWT_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256').decode('UTF-8')

    def setup_method(self, _):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self, _):
        os.environ.pop('JWT_SECRET')

    def test_garage_door_status__should_call_get_status(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_controller.get_status.return_value = self.STATUS

        get_garage_door_status(self.USER_ID, self.GARAGE_ID)

        mock_controller.get_status.assert_called_with(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

    def test_garage_door_status__should_return_success_status_code(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_controller.get_status.return_value = self.STATUS
        actual = get_garage_door_status(self.USER_ID, self.GARAGE_ID)

        assert actual.status_code == 200

    def test_garage_door_status__should_return_success_header(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_controller.get_status.return_value = self.STATUS
        expected_headers = 'application/json'

        actual = get_garage_door_status(self.USER_ID, self.GARAGE_ID)

        assert actual.content_type == expected_headers

    def test_garage_door_status__should_return_response_body(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_controller.get_status.return_value = self.STATUS

        actual = get_garage_door_status(self.USER_ID, self.GARAGE_ID)

        assert actual.data.decode('UTF-8') == self.STATUS.to_json()

    def test_update_garage_door_state__should_call_update_state(self, mock_request, mock_controller):
        expected_data = '{"garageDoorOpen": "True"}'.encode()
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_controller.update_state.return_value = {}
        mock_request.data = expected_data
        update_garage_door_state(self.USER_ID, self.GARAGE_ID)

        mock_controller.update_state.assert_called_with(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID, expected_data )

    def test_update_garage_door_state__should_return_success_status_code(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_request.data = '{"garageDoorOpen": "False"}'.encode()
        mock_controller.update_state.return_value = {}
        actual = update_garage_door_state(self.USER_ID, self.GARAGE_ID)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_success_header(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        mock_request.data = '{"garageDoorOpen": "True"}'.encode()
        mock_controller.update_state.return_value = {}
        expected_headers = 'application/json'

        actual = update_garage_door_state(self.USER_ID, self.GARAGE_ID)

        assert actual.content_type == expected_headers

    def test_update_garage_door_state__should_check_state_with_request(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        post_body = '{"garageDoorOpen": "True"}'
        mock_request.data = post_body.encode()
        expected_response = {'fakeResponse': True}
        mock_controller.update_state.return_value = expected_response

        actual = update_garage_door_state(self.USER_ID, self.GARAGE_ID)
        json_actual = json.loads(actual.data)

        assert json_actual == expected_response

    def test_toggle_garage_door__should_call_controller_with_bearer_token(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        toggle_garage_door(self.USER_ID, self.GARAGE_ID)

        mock_controller.toggle_door.assert_called_with(self.JWT_TOKEN, self.USER_ID, self.GARAGE_ID)

    def test_toggle_garage_door__should_return_success_status_code(self, mock_request, mock_controller):
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        actual = toggle_garage_door(self.USER_ID, self.GARAGE_ID)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_success_headers(self, mock_request, mock_controller):
        expected_headers = 'application/json'
        mock_request.headers = {'Authorization': self.JWT_TOKEN}
        actual = toggle_garage_door(self.USER_ID, self.GARAGE_ID)

        assert actual.content_type == expected_headers
