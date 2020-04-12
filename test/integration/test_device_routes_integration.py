import json
import os
import uuid

import jwt

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserRoles, UserInformation, Roles, RoleDevices
from svc.manager import create_app


class TestDeviceRoutesIntegration:
    TEST_CLIENT = None
    USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    ROLE_NAME = 'made_up_role'
    JWT_SECRET = 'fakeSecret'
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'
    USER_ROLE = None
    USER_INFO = None
    ROLE = None

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET, 'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="fake desc", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=str(uuid.uuid4()), user_id=self.USER_ID, role_id=self.ROLE_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_ROLE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_ROLE)
        with UserDatabaseManager() as database:
            database.session.delete(self.ROLE)
            database.session.delete(self.USER_INFO)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_add_device_by_user_id__should_return_unauthorized(self):
        post_body = '{}'
        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/devices', headers={}, data=post_body)
        assert actual.status_code == 401

    def test_add_device_by_user_id__should_return_success_when_user_with_correct_role(self):
        ip_address = '1.1.1.1'
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        post_body = json.dumps({'roleName': self.ROLE_NAME, 'ipAddress': ip_address})
        header = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/devices', headers=header, data=post_body)

        assert actual.status_code == 200

        with UserDatabaseManager() as database:
            record = database.session.query(RoleDevices).filter_by(ip_address=ip_address).first()
            assert record.ip_address == ip_address
