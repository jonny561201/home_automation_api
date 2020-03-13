import os
import uuid

import jwt
from flask import json
from mock import patch

from svc.manager import create_app


class TestGarageDoorRoutesIntegration:
    TEST_CLIENT = None
    JWT_SECRET = 'testSecret'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_get_garage_door_status__should_return_unauthorized_with_no_header(self):
        actual = self.TEST_CLIENT.get('garageDoor/user/%s/status' % self.USER_ID)

        assert actual.status_code == 401

    @patch('svc.utilities.event_utils.MyThread')
    def test_get_garage_door_status__should_return_success_with_valid_jwt(self, mock_thread):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get('garageDoor/user/%s/status' % self.USER_ID, headers=headers)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_unauthorized_without_jwt(self):
        post_body = {}
        headers = {}

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=post_body, headers=headers)

        assert actual.status_code == 401

    def test_update_garage_door_state__should_return_success(self):
        post_body = {'garageDoorOpen': True}
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_bad_request_when_malformed_json(self):
        post_body = {'badKey': 'fakerequest'}
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 400

    def test_toggle_garage_door__should_return_success(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('garageDoor/user/%s/toggle' % self.USER_ID, headers=headers)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_unauthorized_when_invalid_jwt(self):
        bearer_token = jwt.encode({}, 'bad_secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('garageDoor/user/%s/toggle' % self.USER_ID, headers=headers)

        assert actual.status_code == 401
