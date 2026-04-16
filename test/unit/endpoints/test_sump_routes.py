import json

from flask import Flask
from mock import patch

from svc.models.sump import SumpLevel
from svc.endpoints.sump_routes import get_current_sump_level, save_current_depth
from test.unit.test_helpers import setup_request


class TestSumpRoutes:
    BEARER_TOKEN = 'test123'
    HEADERS = {'Authorization': BEARER_TOKEN}
    API_KEY = 'oi;asdfliuhasdf'

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_call_controller(self, mock_controller):
        mock_controller.return_value = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)

        get_current_sump_level()

        mock_controller.assert_called_with(self.BEARER_TOKEN)

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_return_valid_response(self, mock_controller):
        expected_depth = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)
        mock_controller.return_value = expected_depth

        actual = get_current_sump_level()
        json_actual = json.loads(actual.data)

        assert json_actual == expected_depth.to_dict()

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_return_success_status(self, mock_controller):
        expected_depth = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)
        mock_controller.return_value = expected_depth

        actual = get_current_sump_level()

        assert actual.status_code == 200

    @patch('svc.endpoints.sump_routes.save_current_level')
    def test_save_current_depth__should_call_controller(self, mock_controller):
        request_data = {'depth': 12.5}
        self.ctx = setup_request(self.app, self.ctx, request_data, {'X-API-Key': self.API_KEY})

        save_current_depth()

        mock_controller.assert_called_with(self.API_KEY, request_data)

    @patch('svc.endpoints.sump_routes.save_current_level')
    def test_save_current_depth__should_return_success_status(self, mock_controller):
        request_data = {'depth': 12.5}
        self.ctx = setup_request(self.app, self.ctx, request_data, {'X-API-Key': self.API_KEY})

        actual = save_current_depth()

        assert actual.status_code == 200

