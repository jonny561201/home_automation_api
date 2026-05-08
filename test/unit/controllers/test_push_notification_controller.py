import jwt
import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.config.settings_state import Settings
from svc.constants.home_automation import AuthClaims
from svc.controllers.push_notification_controller import subscribe_user, unsubscribe_user, get_vapid_public_key


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


@patch('svc.controllers.push_notification_controller.PushSubscriptionRepository')
@patch('svc.controllers.push_notification_controller.AuthClient')
class TestUnsubscribeUser:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER_ID = 'fake_user_id'
    ENDPOINT = 'https://fcm.googleapis.com/fcm/send/abc123'

    def setup_method(self):
        self.REQUEST = {'endpoint': self.ENDPOINT}

    def test_unsubscribe_user__should_validate_bearer_token(self, mock_jwt, mock_db):
        unsubscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_unsubscribe_user__should_call_delete_with_user_id_from_claims(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        unsubscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.delete_subscription.assert_called_with(self.USER_ID, ANY)

    def test_unsubscribe_user__should_call_delete_with_endpoint(self, mock_jwt, mock_db):
        unsubscribe_user(self.BEARER_TOKEN, self.REQUEST)

        mock_db.return_value.__enter__.return_value.delete_subscription.assert_called_with(ANY, self.ENDPOINT)

    def test_unsubscribe_user__should_raise_bad_request_when_endpoint_missing(self, mock_jwt, mock_db):
        with pytest.raises(BadRequest):
            unsubscribe_user(self.BEARER_TOKEN, {})


class TestGetVapidPublicKey:
    PUBLIC_KEY = 'BNcfakeVapidPublicKeyValue'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self._original_settings = self.SETTINGS._settings
        self.SETTINGS._settings = {'VapidPublicKey': self.PUBLIC_KEY}

    def teardown_method(self):
        self.SETTINGS._settings = self._original_settings

    def test_get_vapid_public_key__should_return_public_key_from_settings(self):
        actual = get_vapid_public_key()

        assert actual == {'publicKey': self.PUBLIC_KEY}
