import jwt
import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.controllers.push_notification_controller import subscribe_user


@patch('svc.controllers.push_notification_controller.PushSubscriptionRepository')
@patch('svc.controllers.push_notification_controller.AuthClient')
class TestSubscribeUser:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER_ID = 'fake_user_id'
    ENDPOINT = 'https://fcm.googleapis.com/fcm/send/abc123'
    P256DH_KEY = 'BNcvalueforp256dh'
    AUTH_KEY = 'tBHIauthkeyvalue'

    def setup_method(self):
        self.REQUEST = {'endpoint': self.ENDPOINT, 'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}}

    def test_subscribe_user__should_validate_bearer_token(self, mock_jwt, mock_db):
        subscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_subscribe_user__should_call_upsert_with_user_id_from_claims(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        subscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.upsert_subscription.assert_called_with(self.USER_ID, ANY, ANY, ANY)

    def test_subscribe_user__should_call_upsert_with_endpoint(self, mock_jwt, mock_db):
        subscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.upsert_subscription.assert_called_with(ANY, self.ENDPOINT, ANY, ANY)

    def test_subscribe_user__should_call_upsert_with_p256dh_key(self, mock_jwt, mock_db):
        subscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.upsert_subscription.assert_called_with(ANY, ANY, self.P256DH_KEY, ANY)

    def test_subscribe_user__should_call_upsert_with_auth_key(self, mock_jwt, mock_db):
        subscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.upsert_subscription.assert_called_with(ANY, ANY, ANY, self.AUTH_KEY)

    def test_subscribe_user__should_raise_bad_request_when_endpoint_missing(self, mock_jwt, mock_db):
        request = {'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}}
        with pytest.raises(BadRequest):
            subscribe_user(self.BEARER_TOKEN, request)

    def test_subscribe_user__should_raise_bad_request_when_p256dh_missing(self, mock_jwt, mock_db):
        request = {'endpoint': self.ENDPOINT, 'keys': {'auth': self.AUTH_KEY}}
        with pytest.raises(BadRequest):
            subscribe_user(self.BEARER_TOKEN, request)

    def test_subscribe_user__should_raise_bad_request_when_auth_missing(self, mock_jwt, mock_db):
        request = {'endpoint': self.ENDPOINT, 'keys': {'p256dh': self.P256DH_KEY}}
        with pytest.raises(BadRequest):
            subscribe_user(self.BEARER_TOKEN, request)

    def test_subscribe_user__should_raise_bad_request_when_keys_missing(self, mock_jwt, mock_db):
        request = {'endpoint': self.ENDPOINT}
        with pytest.raises(BadRequest):
            subscribe_user(self.BEARER_TOKEN, request)
