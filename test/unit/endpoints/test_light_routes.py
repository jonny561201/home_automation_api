import json

from flask import Flask
from mock import patch

from svc.endpoints.light_routes import get_assigned_light_groups, set_assigned_light_group, set_light_state
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.light_routes.light_controller')
class TestLightRoutes:
    BEARER_TOKEN = 'fakeBearerToken'
    HEADERS = {'Authorization': BEARER_TOKEN}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_get_assigned_light_groups__should_call_get_assigned_lights(self, mock_controller):
        mock_controller.get_assigned_light_groups.return_value = {}
        get_assigned_light_groups()

        mock_controller.get_assigned_light_groups.assert_called_with(self.BEARER_TOKEN)

    def test_get_assigned_light_groups__should_return_success_status_code(self, mock_controller):
        mock_controller.get_assigned_light_groups.return_value = {}
        actual = get_assigned_light_groups()

        assert actual.status_code == 200

    def test_get_assigned_light_groups__should_return_success_headers(self, mock_controller):
        mock_controller.get_assigned_light_groups.return_value = {}
        actual = get_assigned_light_groups()

        assert actual.content_type == 'application/json'

    def test_get_assigned_light_groups__should_response_from_controller(self, mock_controller):
        result = {'response': 'not important'}
        mock_controller.get_assigned_light_groups.return_value = result
        actual = get_assigned_light_groups()

        assert json.loads(actual.data) == result

    def test_set_assigned_light_group__should_call_light_controller(self, mock_controller):
        request_data = {"on": "False", "groupId": 1}
        self.ctx = setup_request(self.app, self.ctx, request_data, self.HEADERS)
        set_assigned_light_group()

        mock_controller.set_assigned_light_groups.assert_called_with(self.BEARER_TOKEN, request_data)

    def test_set_assigned_light_group__should_return_success_status_code(self, mock_controller):
        actual = set_assigned_light_group()

        assert actual.status_code == 200

    def test_set_assigned_light_group__should_return_success_headers(self, mock_controller):
        actual = set_assigned_light_group()

        assert actual.content_type == 'application/json'

    def test_set_light_state__should_call_light_controller(self, mock_controller):
        request_data = {"on": "False", "brightness": 133, "lightId": "3"}
        self.ctx = setup_request(self.app, self.ctx, request_data, self.HEADERS)
        set_light_state()

        mock_controller.set_assigned_light.assert_called_with(self.BEARER_TOKEN, request_data)

    def test_set_light_state__should_return_success_status_code(self, mock_controller):
        actual = set_light_state()

        assert actual.status_code == 200

    def test_set_light_state__should_return_success_headers(self, mock_controller):
        actual = set_light_state()

        assert actual.content_type == 'application/json'
