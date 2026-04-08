import os
import uuid
from datetime import datetime

import jwt
import json
from flask import Flask
from mock import patch

from svc.models.garage import GarageDoor, GarageOverview, GarageStatus, Coordinates, GarageState
from svc.endpoints.garage_door_routes import get_all_garage_door_status, get_garage_door_status, update_garage_door_state, toggle_garage_door


@patch('svc.endpoints.garage_door_routes.garage_door_controller')
class TestAppRoutes:
    GARAGE_ID = 3
    USER_ID = str(uuid.uuid4())
    JWT_SECRET = 'fake_jwt_secret'
    JWT_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256')

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context(data=json.dumps({}), content_type='application/json', headers={'Authorization': self.JWT_TOKEN})
        self.ctx.push()
        self.STATE = GarageState(isGarageOpen=False)
        self.COORDINATES = Coordinates(latitude=19.00, longitude=-99.00)
        self.STATUS = GarageStatus(isGarageOpen=True, statusDuration=datetime.now(), coordinates=self.COORDINATES)
        self.DOORS = [GarageDoor(garageId='1', isGarageOpen=True, statusDuration=datetime.now())]
        self.OVERVIEW = GarageOverview(coordinates=self.COORDINATES, doors=self.DOORS)

    def teardown_method(self):
        self.ctx.pop()
        os.environ.pop('JWT_SECRET')

    def test_get_all_garage_door_status__should_call_get_all_status(self, mock_controller):
        mock_controller.get_all_status.return_value = self.OVERVIEW
        get_all_garage_door_status()

        mock_controller.get_all_status.assert_called_with(self.JWT_TOKEN)

    def test_get_all_garage_door_status__should_return_success_status_code(self, mock_controller):
        mock_controller.get_all_status.return_value = self.OVERVIEW
        actual = get_all_garage_door_status()

        assert actual.status_code == 200

    def test_get_all_garage_door_status__should_return_success_header(self, mock_controller):
        mock_controller.get_all_status.return_value = self.OVERVIEW
        actual = get_all_garage_door_status()

        assert actual.content_type == 'application/json'

    def test_get_all_garage_door_status__should_return_response_body(self, mock_controller):
        mock_controller.get_all_status.return_value = self.OVERVIEW
        actual = get_all_garage_door_status()

        assert actual.data.decode('UTF-8') == self.OVERVIEW.to_json()

    def test_garage_door_status__should_call_get_status(self, mock_controller):
        mock_controller.get_status.return_value = self.STATUS
        get_garage_door_status(self.GARAGE_ID)

        mock_controller.get_status.assert_called_with(self.JWT_TOKEN, self.GARAGE_ID)

    def test_garage_door_status__should_return_success_status_code(self, mock_controller):
        mock_controller.get_status.return_value = self.STATUS
        actual = get_garage_door_status(self.GARAGE_ID)

        assert actual.status_code == 200

    def test_garage_door_status__should_return_success_header(self, mock_controller):
        mock_controller.get_status.return_value = self.STATUS

        actual = get_garage_door_status(self.GARAGE_ID)

        assert actual.content_type == 'application/json'

    def test_garage_door_status__should_return_response_body(self, mock_controller):
        mock_controller.get_status.return_value = self.STATUS

        actual = get_garage_door_status(self.GARAGE_ID)

        assert actual.data.decode('UTF-8') == self.STATUS.to_json()

    def test_update_garage_door_state__should_call_update_state(self, mock_controller):
        expected_data = {"garageDoorOpen": "True"}
        self.ctx.pop()
        self.ctx = self.app.test_request_context(data=json.dumps(expected_data), content_type='application/json', headers={'Authorization': self.JWT_TOKEN})
        self.ctx.push()
        mock_controller.update_state.return_value = self.STATE
        update_garage_door_state(self.GARAGE_ID)

        mock_controller.update_state.assert_called_with(self.JWT_TOKEN, self.GARAGE_ID, expected_data)

    def test_update_garage_door_state__should_return_success_status_code(self, mock_controller):
        mock_controller.update_state.return_value = self.STATE
        actual = update_garage_door_state(self.GARAGE_ID)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_success_header(self, mock_controller):
        mock_controller.update_state.return_value = self.STATE

        actual = update_garage_door_state(self.GARAGE_ID)

        assert actual.content_type == 'application/json'

    def test_update_garage_door_state__should_check_state_with_request(self, mock_controller):
        mock_controller.update_state.return_value = self.STATE

        actual = update_garage_door_state(self.GARAGE_ID)
        json_actual = json.loads(actual.data)

        assert json_actual == self.STATE.to_dict()

    def test_toggle_garage_door__should_call_controller_with_bearer_token(self, mock_controller):
        toggle_garage_door(self.GARAGE_ID)

        mock_controller.toggle_door.assert_called_with(self.JWT_TOKEN, self.GARAGE_ID)

    def test_toggle_garage_door__should_return_success_status_code(self, mock_controller):
        actual = toggle_garage_door(self.GARAGE_ID)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_success_headers(self, mock_controller):
        actual = toggle_garage_door(self.GARAGE_ID)

        assert actual.content_type == 'application/json'
