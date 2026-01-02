import os
import uuid

import jwt
from flask import json
from mock import patch
from requests import Response

from config.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, Roles, UserRoles, RoleDevices, RoleDeviceNodes
from svc.manager import app


@patch('svc.utilities.api_utils.requests')
class TestGarageDoorRoutesIntegration:
    GARAGE_ID = 4
    TEST_CLIENT = None
    JWT_SECRET = 'testSecret'
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'
    USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())

    def setup_method(self):
        settings = Settings.get_instance()
        settings._settings = None
        settings.Database._settings = None
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        os.environ.update({'JWT_SECRET': self.JWT_SECRET, 'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="fake desc", role_name='garage_door')
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID)
        self.DEVICE = RoleDevices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address='1.1.1.1', ip_port=5001)
        with UserDatabaseManager() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_ROLE)
            database.session.add(self.DEVICE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_ROLE)
        with UserDatabaseManager() as database:
            database.session.delete(self.ROLE)
            database.session.delete(self.USER_INFO)
            database.session.query(RoleDeviceNodes).delete()
            database.session.query(RoleDevices).delete()
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_garage_door_status__should_return_unauthorized_with_no_header(self, mock_request):
        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/status'
        actual = self.TEST_CLIENT.get(url)

        assert actual.status_code == 401

    def test_get_garage_door_status__should_return_success_with_valid_jwt(self, mock_request):
        response = Response()
        response._content = json.dumps({'testResponse': 'found it!'}).encode()
        response.status_code = 200
        mock_request.get.return_value = response
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/status'
        actual = self.TEST_CLIENT.get(url, headers=headers)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_unauthorized_without_jwt(self, mock_request):
        post_body = {}
        headers = {}

        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/state'
        actual = self.TEST_CLIENT.post(url, data=post_body, headers=headers)

        assert actual.status_code == 401

    def test_update_garage_door_state__should_return_success(self, mock_request):
        post_body = {'garageDoorOpen': True}
        response = Response()
        response._content = json.dumps({'testResponse': 'found it!'}).encode()
        response.status_code = 200
        mock_request.post.return_value = response
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/state'
        actual = self.TEST_CLIENT.post(url, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_bad_request_when_malformed_json(self, mock_request):
        post_body = {'badKey': 'fakerequest'}
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        response = Response()
        response.status_code = 400
        response._content = json.dumps({}).encode()
        mock_request.post.return_value = response

        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/state'
        actual = self.TEST_CLIENT.post(url, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 400

    def test_toggle_garage_door__should_return_success(self, mock_request):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        response = Response()
        response.status_code = 200
        mock_request.get.return_value = response

        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/toggle'
        actual = self.TEST_CLIENT.get(url, headers=headers)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_unauthorized_when_invalid_jwt(self, mock_request):
        bearer_token = jwt.encode({}, 'bad_secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        url = f'garageDoor/{self.GARAGE_ID}/user/{self.USER_ID}/toggle'
        actual = self.TEST_CLIENT.get(url, headers=headers)

        assert actual.status_code == 401
