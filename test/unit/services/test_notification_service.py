from mock import MagicMock, patch

from svc.services.notification_service import notify_household_for_device, notify_sump_alert


@patch('svc.services.notification_service.send_push_to_subscriptions')
@patch('svc.services.notification_service.PushSubscriptionRepository')
@patch('svc.services.notification_service.DeviceRepository')
class TestNotifyHouseholdForDevice:
    DEVICE_ID = 'device-1234'
    OWNER_ID = 'owner-5678'
    PAYLOAD = {'title': 'hi'}

    def test_notify_household_for_device__should_lookup_owner_by_device(self, mock_device, mock_push, mock_send):
        notify_household_for_device(self.DEVICE_ID, self.PAYLOAD)

        mock_device.return_value.__enter__.return_value.get_user_id_by_device.assert_called_with(self.DEVICE_ID)

    def test_notify_household_for_device__should_skip_when_owner_missing(self, mock_device, mock_push, mock_send):
        mock_device.return_value.__enter__.return_value.get_user_id_by_device.return_value = None

        notify_household_for_device(self.DEVICE_ID, self.PAYLOAD)

        mock_push.return_value.__enter__.return_value.get_subscriptions_for_household.assert_not_called()
        mock_send.assert_not_called()

    def test_notify_household_for_device__should_lookup_subscriptions_for_owner(self, mock_device, mock_push, mock_send):
        mock_device.return_value.__enter__.return_value.get_user_id_by_device.return_value = self.OWNER_ID

        notify_household_for_device(self.DEVICE_ID, self.PAYLOAD)

        mock_push.return_value.__enter__.return_value.get_subscriptions_for_household.assert_called_with(self.OWNER_ID)

    def test_notify_household_for_device__should_skip_send_when_no_subscriptions(self, mock_device, mock_push, mock_send):
        mock_device.return_value.__enter__.return_value.get_user_id_by_device.return_value = self.OWNER_ID
        mock_push.return_value.__enter__.return_value.get_subscriptions_for_household.return_value = []

        notify_household_for_device(self.DEVICE_ID, self.PAYLOAD)

        mock_send.assert_not_called()

    def test_notify_household_for_device__should_send_to_subscriptions(self, mock_device, mock_push, mock_send):
        subscriptions = [MagicMock(), MagicMock()]
        mock_device.return_value.__enter__.return_value.get_user_id_by_device.return_value = self.OWNER_ID
        mock_push.return_value.__enter__.return_value.get_subscriptions_for_household.return_value = subscriptions

        notify_household_for_device(self.DEVICE_ID, self.PAYLOAD)

        mock_send.assert_called_with(subscriptions, self.PAYLOAD)


@patch('svc.services.notification_service.notify_household_for_device')
class TestNotifySumpAlert:
    DEVICE_ID = 'device-1234'

    def test_notify_sump_alert__should_not_notify_when_alert_level_below_warning(self, mock_notify):
        notify_sump_alert(self.DEVICE_ID, 1)

        mock_notify.assert_not_called()

    def test_notify_sump_alert__should_not_notify_when_alert_level_missing(self, mock_notify):
        notify_sump_alert(self.DEVICE_ID, None)

        mock_notify.assert_not_called()

    def test_notify_sump_alert__should_notify_with_warning_payload_when_alert_level_two(self, mock_notify):
        notify_sump_alert(self.DEVICE_ID, 2)

        expected = {'title': 'Sump Pump Warning', 'body': 'Elevated water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 2}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)

    def test_notify_sump_alert__should_notify_with_alert_payload_when_alert_level_three(self, mock_notify):
        notify_sump_alert(self.DEVICE_ID, 3)

        expected = {'title': 'Sump Pump Alert', 'body': 'Critical water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 3}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)
