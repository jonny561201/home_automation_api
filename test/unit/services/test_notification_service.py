from datetime import datetime

from mock import MagicMock, patch

from svc.services.notification_service import notify_garage_alert, notify_household_for_device, notify_sump_alert


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
@patch('svc.services.notification_service.DeviceAlertStateRepository')
class TestNotifySumpAlert:
    DEVICE_ID = 'device-1234'
    ALERT_KEY = 'sump:level'

    def test_notify_sump_alert__should_not_touch_state_when_alert_level_missing(self, mock_repo, mock_notify):
        notify_sump_alert(self.DEVICE_ID, None)

        mock_repo.return_value.__enter__.return_value.get_last_notified.assert_not_called()
        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_not_called()
        mock_notify.assert_not_called()

    def test_notify_sump_alert__should_skip_when_level_unchanged(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = '2'

        notify_sump_alert(self.DEVICE_ID, 2)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_not_called()
        mock_notify.assert_not_called()

    def test_notify_sump_alert__should_record_state_but_not_notify_when_level_below_warning(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = '2'

        notify_sump_alert(self.DEVICE_ID, 1)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY, '1')
        mock_notify.assert_not_called()

    def test_notify_sump_alert__should_notify_with_warning_payload_when_level_changes_to_two(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = '0'

        notify_sump_alert(self.DEVICE_ID, 2)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY, '2')
        expected = {'title': 'Sump Pump Warning', 'body': 'Elevated water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 2}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)

    def test_notify_sump_alert__should_notify_with_alert_payload_when_level_changes_to_three(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = '2'

        notify_sump_alert(self.DEVICE_ID, 3)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY, '3')
        expected = {'title': 'Sump Pump Alert', 'body': 'Critical water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 3}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)

    def test_notify_sump_alert__should_notify_when_re_armed_after_normal(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = '0'

        notify_sump_alert(self.DEVICE_ID, 2)

        expected = {'title': 'Sump Pump Warning', 'body': 'Elevated water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 2}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)

    def test_notify_sump_alert__should_notify_first_reading_when_no_prior_state(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = None

        notify_sump_alert(self.DEVICE_ID, 2)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY, '2')
        expected = {'title': 'Sump Pump Warning', 'body': 'Elevated water level detected in the sump pit.', 'tag': 'sump-alert', 'data': {'warningLevel': 2}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)


@patch('svc.services.notification_service.notify_household_for_device')
@patch('svc.services.notification_service.DeviceAlertStateRepository')
class TestNotifyGarageAlert:
    DEVICE_ID = 'device-1234'
    GARAGE_ID = '3'
    DOOR_NAME = 'Left Garage'
    DURATION = datetime(2025, 1, 1, 12, 0, 0)
    PRIOR_DURATION = datetime(2024, 12, 31, 8, 0, 0)
    ALERT_KEY = f'garage:{GARAGE_ID}'

    def test_notify_garage_alert__should_lookup_last_notified(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = None

        notify_garage_alert(self.DEVICE_ID, self.GARAGE_ID, self.DOOR_NAME, self.DURATION)

        mock_repo.return_value.__enter__.return_value.get_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY)

    def test_notify_garage_alert__should_skip_when_already_notified_for_duration(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = self.DURATION.isoformat()

        notify_garage_alert(self.DEVICE_ID, self.GARAGE_ID, self.DOOR_NAME, self.DURATION)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_not_called()
        mock_notify.assert_not_called()

    def test_notify_garage_alert__should_upsert_duration_when_new_opening(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = self.PRIOR_DURATION.isoformat()

        notify_garage_alert(self.DEVICE_ID, self.GARAGE_ID, self.DOOR_NAME, self.DURATION)

        mock_repo.return_value.__enter__.return_value.upsert_last_notified.assert_called_with(self.DEVICE_ID, self.ALERT_KEY, self.DURATION.isoformat())

    def test_notify_garage_alert__should_notify_household_when_new_opening(self, mock_repo, mock_notify):
        mock_repo.return_value.__enter__.return_value.get_last_notified.return_value = None

        notify_garage_alert(self.DEVICE_ID, self.GARAGE_ID, self.DOOR_NAME, self.DURATION)

        expected = {'title': 'Garage Door Alert', 'body': f'{self.DOOR_NAME} has been open longer than the alert time.', 'tag': f'garage-alert-{self.GARAGE_ID}', 'data': {'garageId': self.GARAGE_ID}}
        mock_notify.assert_called_with(self.DEVICE_ID, expected)
