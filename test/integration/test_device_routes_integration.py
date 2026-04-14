import json
import uuid

from sqlalchemy import delete, select

from test.integration.integration_helpers import mock_jwks_token
from svc.db.models.user_information_model import DeviceType
from svc.db.models.user_information_model import UserInformation, Devices, DeviceNodes
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestDeviceRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())
    ROLE_NAME = 'made_up_role'
    IP_ADDRESS = '192.1.1.1'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADER = {'Authorization': self.TOKEN, 'Content-Type': 'application/json'}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        with DatabaseBase() as database:
            device_type = database.session.execute(select(DeviceType).where(DeviceType.type == 'lighting')).scalars().first()
            self.DEVICE = Devices(ip_address=self.IP_ADDRESS, ip_port=2, name='sample', api_key='test-key', device_type_id=device_type.id, user_id=self.USER_ID)
            database.session.add(self.USER_INFO)
            database.session.commit()
            database.session.add(self.DEVICE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DeviceNodes))
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_add_device__should_return_unauthorized(self):
        actual = self.TEST_CLIENT.post(f'devices/register', headers={'Content-Type': 'application/json'}, data='{}')
        assert actual.status_code == 401

    def test_add_device__should_return_device_id_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address, 'ipPort': 50})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert json.loads(actual.data)['deviceId'] is not None

    def test_add_device__should_return_success_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address, 'ipPort': 501})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert actual.status_code == 200

        with DatabaseBase() as database:
            record = database.session.execute(select(Devices).where(Devices.ip_address == ip_address)).scalars().first()
            assert record.ip_address == ip_address

    def test_get_devices__should_return_unauthorized(self):
        actual = self.TEST_CLIENT.get(f'devices/devices', headers={'Content-Type': 'application/json'})
        assert actual.status_code == 401

    def test_get_devices__should_return_devices_for_user(self):
        actual = self.TEST_CLIENT.get(f'devices/devices', headers=self.HEADER)

        assert actual.status_code == 200
        assert len(actual.json['devices']) == 1
        assert actual.json['devices'][0]['name'] == 'sample'
