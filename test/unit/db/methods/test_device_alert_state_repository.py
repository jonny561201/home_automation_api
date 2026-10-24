import mock
from sqlalchemy import orm

from svc.db.repositories.device_alert_state_repository import DeviceAlertStateRepository


class TestDeviceAlertStateRepository:
    DEVICE_ID = 'device-1234'
    ALERT_KEY = 'garage:3'
    LAST_NOTIFIED = '2025-01-01T12:00:00'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = DeviceAlertStateRepository()
        self.DATABASE.session = self.SESSION

    def test_get_last_notified__should_return_value_when_record_exists(self):
        record = mock.MagicMock()
        record.last_notified = self.LAST_NOTIFIED
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = record

        actual = self.DATABASE.get_last_notified(self.DEVICE_ID, self.ALERT_KEY)

        self.SESSION.execute.assert_called_once()
        assert actual == self.LAST_NOTIFIED

    def test_get_last_notified__should_return_none_when_no_record(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None

        actual = self.DATABASE.get_last_notified(self.DEVICE_ID, self.ALERT_KEY)

        assert actual is None

    def test_upsert_last_notified__should_execute_statement(self):
        self.DATABASE.upsert_last_notified(self.DEVICE_ID, self.ALERT_KEY, self.LAST_NOTIFIED)

        self.SESSION.execute.assert_called_once()
