import json
import uuid

import jwt
from sqlalchemy import delete, select

from svc.db.repositories.database_base import DatabaseBase
from svc.config.settings_state import Settings
from svc.db.models.user_information_model import UserRoles, UserInformation, Roles, RoleDevices, RoleDeviceNodes
from svc.manager import app


class TestDeviceRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())
    ROLE_NAME = 'made_up_role'
    JWT_SECRET = 'fakeSecret'
    BEARER_TOKEN = jwt.encode({'sub': USER_ID}, JWT_SECRET, algorithm='HS256')
    HEADER = {'Authorization': BEARER_TOKEN, 'Content-Type': 'application/json'}

    def setup_method(self):
        Settings.get_instance()._settings = {'JwtSecret': self.JWT_SECRET}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="fake desc", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID)
        with DatabaseBase() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_ROLE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == self.DEVICE_ID))
            database.session.execute(delete(RoleDevices).where(RoleDevices.user_role_id == self.USER_ROLE_ID))
            database.session.execute(delete(UserRoles).where(UserRoles.id == self.USER_ROLE_ID))
            database.session.execute(delete(Roles).where(Roles.id == self.ROLE_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_add_device_by_user_id__should_return_unauthorized(self):
        actual = self.TEST_CLIENT.post(f'devices/register', headers={'Content-Type': 'application/json'}, data='{}')
        assert actual.status_code == 401

    def test_add_device_by_user_id__should_return_device_id_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert json.loads(actual.data)['deviceId'] is not None

    def test_add_device_by_user_id__should_return_success_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address})
        actual = self.TEST_CLIENT.post(f'devices/register', headers=self.HEADER, data=post_body)

        assert actual.status_code == 200

        with DatabaseBase() as database:
            record = database.session.execute(select(RoleDevices).where(RoleDevices.ip_address == ip_address)).scalars().first()
            assert record.ip_address == ip_address

    def test_add_device_node_by_user_id__should_return_unauthorized(self):
        actual = self.TEST_CLIENT.post(f'devices/{self.DEVICE_ID}/node', headers={'Content-Type': 'application/json'}, data='{}')
        assert actual.status_code == 401

    def test_add_device_node_by_user_id__should_return_success_when_adding_node(self):
        with DatabaseBase() as database:
            device = RoleDevices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address='1.1.1.1')
            database.session.add(device)
        node_name = 'test_node'
        post_body = json.dumps({'nodeName': node_name})
        actual = self.TEST_CLIENT.post(f'devices/{self.DEVICE_ID}/node', headers=self.HEADER, data=post_body)

        assert actual.status_code == 200

        with DatabaseBase() as database:
            actual_record = database.session.execute(select(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == self.DEVICE_ID)).scalars().first()
            assert actual_record.node_name == node_name
