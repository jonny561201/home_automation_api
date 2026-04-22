import json
import uuid

import jwt
from mock import patch
from requests import Response
from sqlalchemy import delete, select

from svc.db.models.user_information_model import UserInformation, Devices, DeviceType, DeviceNodes
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import create_app
from test.integration.integration_helpers import mock_jwks_token


@patch('svc.utilities.api_utils.requests')
class TestGarageDoorRoutesIntegration:
    GARAGE_ID = 4
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADERS = {'Authorization': self.TOKEN, 'Content-Type': 'application/json'}
        flask_app = create_app()
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        with DatabaseBase() as database:
            stmt = select(DeviceType).where(DeviceType.type == 'garage_door')
            type = database.session.execute(stmt).scalars().first()
            self.DEVICE = Devices(user_id=self.USER_ID, registered=False, ip_address='1.1.1.1', name='test', api_key='test-key', device_type_id=type.id)

            database.session.add(self.USER_INFO)
            database.session.commit()
            database.session.add(self.DEVICE)
            database.session.flush()
            self.NODE = DeviceNodes(device_id=self.DEVICE.id, node_device=self.GARAGE_ID, node_name='test')
            database.session.add(self.NODE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DeviceNodes))
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

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
