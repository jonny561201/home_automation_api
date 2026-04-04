import json
import uuid

from mock import patch

from test.integration.integration_helpers import mock_jwks_token
from svc.manager import app


class TestLightRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    LIGHT_PASS = 'fakeLightSecret'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADER = {'Authorization': self.TOKEN, 'Content-Type': 'application/json'}

        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()

    def test_get_all_assigned_lights__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.get('lights/groups')

        assert actual.status_code == 401

    @patch('svc.controllers.light_controller.api_utils')
    def test_get_all_assigned_lights__should_return_success_with_valid_jwt(self, mock_get):
        mock_get.get_light_groups.return_value = {'test': 'fake'}

        actual = self.TEST_CLIENT.get('lights/groups', headers=self.HEADER)

        assert actual.status_code == 200
        assert json.loads(actual.data) == {'test': 'fake'}

    def test_set_assigned_light_group__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.post('lights/group/state', data='{}', headers={'Content-Type': 'application/json'})

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.set_light_groups')
    def test_set_assigned_light_group__should_return_success_with_valid_jwt(self, mock_groups):
        post_body = '{"on": "False", "brightness": 144, "groupId": 1}'
        actual = self.TEST_CLIENT.post('lights/group/state', data=post_body, headers=self.HEADER)

        assert actual.status_code == 200

    def test_set_light_state__should_return_unauthorized_without_header(self):
        actual = self.TEST_CLIENT.post('lights/group/light', headers={'Content-Type': 'application/json'}, data='{}')

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.set_light_state')
    def test_set_light_state__should_return_success_with_valid_jwt(self, mock_groups):
        post_body = '{"on": "True", "brightness": 1, "lightId": "3"}'
        actual = self.TEST_CLIENT.post('lights/group/light', headers=self.HEADER, data=post_body)

        assert actual.status_code == 200
