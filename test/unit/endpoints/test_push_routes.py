from flask import Flask
from mock import patch, ANY

from svc.endpoints.push_routes import subscribe
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.push_routes.push_notification_controller')
class TestPushRoutes:
    FAKE_JWT_TOKEN = 'fakeJwtToken'
    HEADERS = {'Authorization': FAKE_JWT_TOKEN}
    REQUEST = {'endpoint': 'https://fcm.googleapis.com/fcm/send/abc', 'keys': {'p256dh': 'p', 'auth': 'a'}}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, request=self.REQUEST, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_subscribe__should_call_controller_with_bearer_token(self, mock_controller):
        subscribe()

        mock_controller.subscribe_user.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_subscribe__should_call_controller_with_request_body(self, mock_controller):
        subscribe()

        mock_controller.subscribe_user.assert_called_with(ANY, self.REQUEST)

    def test_subscribe__should_return_success_status_code(self, mock_controller):
        actual = subscribe()

        assert actual.status_code == 200

    def test_subscribe__should_return_json_content_type(self, mock_controller):
        actual = subscribe()

        assert actual.content_type == 'application/json'
