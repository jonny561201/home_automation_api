import json

from mock import MagicMock, patch
from pywebpush import WebPushException

from svc.config.settings_state import Settings
from svc.utilities.push_notification_utils import send_push_to_subscriptions


@patch('svc.utilities.push_notification_utils.PushSubscriptionRepository')
@patch('svc.utilities.push_notification_utils.webpush')
class TestSendPushToSubscriptions:
    PRIVATE_KEY = 'fake_private_key'
    SUBJECT = 'mailto:test@example.com'
    PAYLOAD = {'title': 'hello', 'body': 'world'}

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self._original_settings = self.SETTINGS._settings
        self.SETTINGS._settings = {'VapidPrivateKey': self.PRIVATE_KEY, 'VapidSubject': self.SUBJECT}
        self.SUBSCRIPTION = MagicMock(endpoint='https://fcm.googleapis.com/fcm/send/abc', p256dh_key='p256', auth_key='auth')

    def teardown_method(self):
        self.SETTINGS._settings = self._original_settings

    def test_send_push_to_subscriptions__should_skip_when_subscriptions_empty(self, mock_webpush, mock_db):
        send_push_to_subscriptions([], self.PAYLOAD)

        mock_webpush.assert_not_called()

    def test_send_push_to_subscriptions__should_call_webpush_with_subscription_info(self, mock_webpush, mock_db):
        send_push_to_subscriptions([self.SUBSCRIPTION], self.PAYLOAD)

        expected_info = {'endpoint': self.SUBSCRIPTION.endpoint, 'keys': {'p256dh': self.SUBSCRIPTION.p256dh_key, 'auth': self.SUBSCRIPTION.auth_key}}
        mock_webpush.assert_called_with(subscription_info=expected_info, data=json.dumps(self.PAYLOAD), vapid_private_key=self.PRIVATE_KEY, vapid_claims={'sub': self.SUBJECT})

    def test_send_push_to_subscriptions__should_call_webpush_for_each_subscription(self, mock_webpush, mock_db):
        second = MagicMock(endpoint='https://other', p256dh_key='p2', auth_key='a2')

        send_push_to_subscriptions([self.SUBSCRIPTION, second], self.PAYLOAD)

        assert mock_webpush.call_count == 2

    def test_send_push_to_subscriptions__should_delete_subscription_when_endpoint_gone(self, mock_webpush, mock_db):
        response = MagicMock(status_code=410)
        mock_webpush.side_effect = WebPushException('gone', response=response)

        send_push_to_subscriptions([self.SUBSCRIPTION], self.PAYLOAD)

        mock_db.return_value.__enter__.return_value.delete_subscription_by_endpoint.assert_called_with(self.SUBSCRIPTION.endpoint)

    def test_send_push_to_subscriptions__should_delete_subscription_when_endpoint_not_found(self, mock_webpush, mock_db):
        response = MagicMock(status_code=404)
        mock_webpush.side_effect = WebPushException('not found', response=response)

        send_push_to_subscriptions([self.SUBSCRIPTION], self.PAYLOAD)

        mock_db.return_value.__enter__.return_value.delete_subscription_by_endpoint.assert_called_with(self.SUBSCRIPTION.endpoint)

    def test_send_push_to_subscriptions__should_not_delete_subscription_on_other_errors(self, mock_webpush, mock_db):
        response = MagicMock(status_code=500)
        mock_webpush.side_effect = WebPushException('boom', response=response)

        send_push_to_subscriptions([self.SUBSCRIPTION], self.PAYLOAD)

        mock_db.return_value.__enter__.return_value.delete_subscription_by_endpoint.assert_not_called()

    def test_send_push_to_subscriptions__should_continue_after_failure(self, mock_webpush, mock_db):
        response = MagicMock(status_code=500)
        second = MagicMock(endpoint='https://other', p256dh_key='p2', auth_key='a2')
        mock_webpush.side_effect = [WebPushException('boom', response=response), None]

        send_push_to_subscriptions([self.SUBSCRIPTION, second], self.PAYLOAD)

        assert mock_webpush.call_count == 2
