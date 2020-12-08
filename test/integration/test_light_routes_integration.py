import os

import jwt
from mock import patch

from svc.manager import create_app


class TestLightRoutesIntegration:
    TEST_CLIENT = None
    JWT_SECRET = 'fakeSecret'
    LIGHT_USER = 'fakeLightUser'
    LIGHT_PASS = 'fakeLightSecret'

    def setup_method(self):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET, 'LIGHT_API_USERNAME': self.LIGHT_USER, 'LIGHT_API_PASSWORD': self.LIGHT_PASS})
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()

    def teardown_method(self):
        os.environ.pop('JWT_SECRET')

    def test_get_all_assigned_lights__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.get('lights/groups')

        assert actual.status_code == 401

    @patch('svc.controllers.light_controller.api_utils')
    @patch('svc.constants.lights_state.get_light_api_key')
    def test_get_all_assigned_lights__should_return_success_with_valid_jwt(self, mock_api_key, mock_get):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        header = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('lights/groups', headers=header)

        assert actual.status_code == 200

    def test_set_assigned_light_group__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.post('lights/group/state', data='{}', headers={})

        assert actual.status_code == 401

    @patch('svc.constants.lights_state.get_light_api_key')
    def test_set_assigned_light_group__should_return_success_with_valid_jwt(self, mock_api):
        post_body = '{"on": "False", "brightness": 144, "groupId": 1}'
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        header = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.post('lights/group/state', data=post_body, headers=header)

        assert actual.status_code == 200

    def test_set_light_state__should_return_unauthorized_without_header(self):
        post_body = '{}'
        actual = self.TEST_CLIENT.post('lights/group/light', headers={}, data=post_body)

        assert actual.status_code == 401

    @patch('svc.constants.lights_state.get_light_api_key')
    def test_set_light_state__should_return_success_with_valid_jwt(self, mock_api):
        post_body = '{"on": "True", "brightness": 1, "lightId": "3"}'
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        header = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.post('lights/group/light', headers=header, data=post_body)

        assert actual.status_code == 200
