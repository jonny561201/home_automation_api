import json

from flask import Flask
from mock import patch, ANY

from svc.endpoints.push_routes import subscribe, unsubscribe, vapid_key
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.push_routes.push_notification_controller')
class TestSubscribeRoute:
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


@patch('svc.endpoints.push_routes.push_notification_controller')
class TestUnsubscribeRoute:
    FAKE_JWT_TOKEN = 'fakeJwtToken'
    HEADERS = {'Authorization': FAKE_JWT_TOKEN}
    REQUEST = {'endpoint': 'https://fcm.googleapis.com/fcm/send/abc'}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, request=self.REQUEST, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_unsubscribe__should_call_controller_with_bearer_token(self, mock_controller):
        unsubscribe()

        mock_controller.unsubscribe_user.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_unsubscribe__should_call_controller_with_request_body(self, mock_controller):
        unsubscribe()

        mock_controller.unsubscribe_user.assert_called_with(ANY, self.REQUEST)

    def test_unsubscribe__should_return_success_status_code(self, mock_controller):
        actual = unsubscribe()

        assert actual.status_code == 200


@patch('svc.endpoints.push_routes.push_notification_controller')
class TestVapidKeyRoute:
    PUBLIC_KEY = 'BNcfakeVapidPublicKeyValue'

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app)

    def teardown_method(self):
        self.ctx.pop()

    def test_vapid_key__should_call_controller(self, mock_controller):
        mock_controller.get_vapid_public_key.return_value = {'publicKey': self.PUBLIC_KEY}
        vapid_key()

        mock_controller.get_vapid_public_key.assert_called_once()

    def test_vapid_key__should_return_controller_response(self, mock_controller):
        mock_controller.get_vapid_public_key.return_value = {'publicKey': self.PUBLIC_KEY}
        actual = vapid_key()

        assert json.loads(actual.data) == {'publicKey': self.PUBLIC_KEY}

    def test_vapid_key__should_return_success_status_code(self, mock_controller):
        mock_controller.get_vapid_public_key.return_value = {'publicKey': self.PUBLIC_KEY}
        actual = vapid_key()

        assert actual.status_code == 200
