import json
import uuid
from datetime import datetime

import jwt
from mock import patch
from requests import Response
from sqlalchemy import delete

from integration.route_base import mock_jwks_token
from svc.db.models.user_information_model import UserInformation, Roles, UserRoles, Devices, RoleDeviceNodes
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


@patch('svc.utilities.api_utils.requests')
class TestGarageDoorRoutesIntegration:
    GARAGE_ID = 4
    USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADERS = {'Authorization': self.TOKEN, 'Content-Type': 'application/json'}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="fake desc", role_name='garage_door')
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID)
        self.DEVICE = Devices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address='1.1.1.1', ip_port=5001)
        with DatabaseBase() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_ROLE)
            database.session.add(self.DEVICE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.delete(self.USER_ROLE)
        with DatabaseBase() as database:
            database.session.execute(delete(RoleDeviceNodes))
            database.session.execute(delete(Devices).where(Devices.id == self.DEVICE_ID))
            database.session.execute(delete(Roles).where(Roles.id == self.ROLE_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_garage_door_status__should_return_unauthorized_with_no_header(self, mock_request):
        actual = self.TEST_CLIENT.get(f'garageDoor/{self.GARAGE_ID}/status')

        assert actual.status_code == 401

    def test_get_garage_door_status__should_return_success_with_valid_jwt(self, mock_request):
        response = Response()
        response._content = json.dumps({'isGarageOpen': False, 'statusDuration': datetime.now().isoformat(), 'coordinates': {'latitude': 1.12, 'longitude': -12.93}}).encode()
        response.status_code = 200
        mock_request.get.return_value = response
        actual = self.TEST_CLIENT.get(f'garageDoor/{self.GARAGE_ID}/status', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_unauthorized_without_jwt(self, mock_request):
        headers = {'Content-Type': 'application/json'}

        actual = self.TEST_CLIENT.post(f'garageDoor/{self.GARAGE_ID}/state', data='{}', headers=headers)

        assert actual.status_code == 401

    def test_update_garage_door_state__should_return_success(self, mock_request):
        post_body = {'garageDoorOpen': True}

        url = f'garageDoor/{self.GARAGE_ID}/state'
        actual = self.TEST_CLIENT.post(url, data=json.dumps(post_body), headers=self.HEADERS)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_bad_request_when_malformed_json(self, mock_request):
        post_body = {'badKey': 'fakerequest'}

        actual = self.TEST_CLIENT.post(f'garageDoor/{self.GARAGE_ID}/state', data=json.dumps(post_body), headers=self.HEADERS)

        assert actual.status_code == 400

    def test_toggle_garage_door__should_return_success(self, mock_request):
        response = Response()
        response.status_code = 200
        mock_request.get.return_value = response

        actual = self.TEST_CLIENT.get(f'garageDoor/{self.GARAGE_ID}/toggle', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_unauthorized_when_invalid_jwt(self, mock_request):
        bearer_token = jwt.encode({}, 'bad_secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'garageDoor/{self.GARAGE_ID}/toggle', headers=headers)

        assert actual.status_code == 401
