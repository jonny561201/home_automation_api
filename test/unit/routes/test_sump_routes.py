import json

from flask import Flask, request
from mock import patch

from svc.models.sump import SumpLevel
from svc.endpoints.sump_routes import get_current_sump_level, save_current_level_by_user


class TestSumpRoutes:
    BEARER_TOKEN = 'test123'

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context(data=json.dumps({}), headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_call_controller(self, mock_controller):
        user_id = 'fakeuserid'
        mock_controller.return_value = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)

        get_current_sump_level(user_id)

        mock_controller.assert_called_with(user_id, self.BEARER_TOKEN)

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_return_valid_response(self, mock_controller):
        user_id = 'fakeuserid'
        expected_depth = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)
        mock_controller.return_value = expected_depth

        actual = get_current_sump_level(user_id)
        json_actual = json.loads(actual.data)

        assert json_actual == expected_depth.to_dict()

    @patch('svc.endpoints.sump_routes.get_sump_level')
    def test_get_current_sump_level__should_return_success_status(self, mock_controller):
        user_id = 'fakeuserid'
        expected_depth = SumpLevel(currentDepth=1.12, averageDepth=1.23, warningLevel=1)
        mock_controller.return_value = expected_depth

        actual = get_current_sump_level(user_id)

        assert actual.status_code == 200

    @patch('svc.endpoints.sump_routes.save_current_level')
    def test_save_current_level_by_user__should_call_controller(self, mock_controller):
        user_id = 1234
        request_data = json.dumps({}).encode()
        request.data = request_data

        save_current_level_by_user(user_id)

        mock_controller.assert_called_with(user_id, self.BEARER_TOKEN, request_data)
