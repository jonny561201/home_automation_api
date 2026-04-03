import json
import uuid

from sqlalchemy import delete, select

from integration.integration_helpers import mock_jwks_token
from svc.db.models.user_information_model import UserInformation, Devices
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestDeviceRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())
    ROLE_NAME = 'made_up_role'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADER = {'Authorization': self.TOKEN, 'Content-Type': 'application/json'}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        with DatabaseBase() as database:
            database.session.add(self.USER_INFO)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_add_device__should_return_unauthorized(self):
        actual = self.TEST_CLIENT.post(f'devices/register', headers={'Content-Type': 'application/json'}, data='{}')
        assert actual.status_code == 401

    def test_add_device__should_return_device_id_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert json.loads(actual.data)['deviceId'] is not None

    def test_add_device__should_return_success_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert actual.status_code == 200

        with DatabaseBase() as database:
            record = database.session.execute(select(Devices).where(Devices.ip_address == ip_address)).scalars().first()
            assert record.ip_address == ip_address
