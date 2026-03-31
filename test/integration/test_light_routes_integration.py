import json

import jwt
from mock import patch

from svc.config.settings_state import Settings
from svc.manager import app


class TestLightRoutesIntegration:
    JWT_SECRET = 'TotallyNewFakeSecret'
    LIGHT_PASS = 'fakeLightSecret'
    BEARER_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256')
    HEADERS = {'Cookie': f'access_token={BEARER_TOKEN}', 'Content-Type': 'application/json'}

    def setup_method(self):
        Settings.get_instance()._settings = {'JwtSecret': self.JWT_SECRET, 'LightApiKey': self.LIGHT_PASS}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()

    def test_get_all_assigned_lights__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.get('lights/groups')

        assert actual.status_code == 401

    @patch('svc.controllers.light_controller.api_utils')
    def test_get_all_assigned_lights__should_return_success_with_valid_jwt(self, mock_get):
        mock_get.get_light_groups.return_value = {'test': 'fake'}

        actual = self.TEST_CLIENT.get('lights/groups', headers=self.HEADERS)

        assert actual.status_code == 200
        assert json.loads(actual.data) == {'test': 'fake'}

    def test_set_assigned_light_group__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.post('lights/group/state', data='{}', headers={'Content-Type': 'application/json'})

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.set_light_groups')
    def test_set_assigned_light_group__should_return_success_with_valid_jwt(self, mock_groups):
        post_body = '{"on": "False", "brightness": 144, "groupId": 1}'
        actual = self.TEST_CLIENT.post('lights/group/state', data=post_body, headers=self.HEADERS)

        assert actual.status_code == 200

    def test_set_light_state__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.post('lights/group/light', headers={'Content-Type': 'application/json'}, data='{}')

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.set_light_state')
    def test_set_light_state__should_return_success_with_valid_jwt(self, mock_groups):
        post_body = '{"on": "True", "brightness": 1, "lightId": "3"}'
        actual = self.TEST_CLIENT.post('lights/group/light', headers=self.HEADERS, data=post_body)

        assert actual.status_code == 200
