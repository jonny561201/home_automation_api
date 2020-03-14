import os
import uuid

import jwt
from flask import json
from mock import patch
from requests import Response

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

    @patch('svc.utilities.api_utils.requests')
    def test_get_garage_door_status__should_return_success_with_valid_jwt(self, mock_request):
        response = Response()
        response._content = json.dumps({'testResponse': 'found it!'}).encode()
        response.status_code = 200
        mock_request.get.return_value = response
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get('garageDoor/user/%s/status' % self.USER_ID, headers=headers)

        assert actual.status_code == 200

    def test_update_garage_door_state__should_return_unauthorized_without_jwt(self):
        post_body = {}
        headers = {}

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=post_body, headers=headers)

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.requests')
    def test_update_garage_door_state__should_return_success(self, mock_request):
        post_body = {'garageDoorOpen': True}
        response = Response()
        response._content = json.dumps({'testResponse': 'found it!'}).encode()
        response.status_code = 200
        mock_request.post.return_value = response
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 200

    @patch('svc.utilities.api_utils.requests')
    def test_update_garage_door_state__should_return_bad_request_when_malformed_json(self, mock_request):
        post_body = {'badKey': 'fakerequest'}
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        response = Response()
        response.status_code = 400
        response._content = json.dumps({}).encode()
        mock_request.post.return_value = response

        actual = self.TEST_CLIENT.post('garageDoor/user/%s/state' % self.USER_ID, data=json.dumps(post_body), headers=headers)

        assert actual.status_code == 400

    @patch('svc.utilities.api_utils.requests')
    def test_toggle_garage_door__should_return_success(self, mock_request):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        response = Response()
        response.status_code = 200
        mock_request.get.return_value = response

        actual = self.TEST_CLIENT.get('garageDoor/user/%s/toggle' % self.USER_ID, headers=headers)

        assert actual.status_code == 200

    def test_toggle_garage_door__should_return_unauthorized_when_invalid_jwt(self):
        bearer_token = jwt.encode({}, 'bad_secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('garageDoor/user/%s/toggle' % self.USER_ID, headers=headers)

        assert actual.status_code == 401
