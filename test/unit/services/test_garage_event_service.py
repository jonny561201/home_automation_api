from mock import patch
import pytest
from werkzeug.exceptions import FailedDependency

from svc.models.devices import DeviceInfo
from svc.services.garage_event_service import GarageEventBroadcaster


class TestGarageEventBroadcaster:
    STATUS = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': []}

    def setup_method(self):
        self.broadcaster = GarageEventBroadcaster._decorated()

    def test_latest__should_start_with_no_status(self):
        assert self.broadcaster.latest() == (0, None)

    def test_publish__should_store_status_and_increment_version(self):
        self.broadcaster.publish(self.STATUS)

        assert self.broadcaster.latest() == (1, self.STATUS)

    def test_wait_for_update__should_return_latest_when_version_already_ahead(self):
        self.broadcaster.publish(self.STATUS)

        actual = self.broadcaster.wait_for_update(0, 0.01)

        assert actual == (1, self.STATUS)

    def test_wait_for_update__should_return_none_on_timeout(self):
        actual = self.broadcaster.wait_for_update(0, 0.01)

        assert actual is None

    @patch('svc.services.garage_event_service.threading.Thread')
    def test_start__should_start_daemon_thread(self, mock_thread):
        self.broadcaster.start()

        assert mock_thread.call_args.kwargs['daemon'] is True
        mock_thread.return_value.start.assert_called_once()


@patch('svc.services.garage_event_service.api_utils')
@patch('svc.services.garage_event_service.DeviceRepository')
class TestConsumeUpstream:
    STATUS = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': []}
    DEVICE_INFO = DeviceInfo(id='fake-device-id', ip_address='1.1.1.1', ip_port=5001, api_key='fake-api-key')

    def setup_method(self):
        self.broadcaster = GarageEventBroadcaster._decorated()

    def test_consume_upstream__should_stream_from_registered_garage_device(self, mock_db, mock_api):
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_api.stream_garage_door_events.return_value = []

        self.broadcaster.consume_upstream()

        mock_db.return_value.__enter__.return_value.get_device_info.assert_called_with('garage_door')
        mock_api.stream_garage_door_events.assert_called_with('fake-api-key', 'http://1.1.1.1:5001')

    def test_consume_upstream__should_publish_each_streamed_status(self, mock_db, mock_api):
        second = {'coordinates': {'latitude': 1.0, 'longitude': 2.0}, 'doors': [{'garageId': '1'}]}
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_api.stream_garage_door_events.return_value = [self.STATUS, second]

        self.broadcaster.consume_upstream()

        assert self.broadcaster.latest() == (2, second)

    def test_consume_upstream__should_raise_failed_dependency_when_device_not_registered(self, mock_db, mock_api):
        mock_db.return_value.__enter__.return_value.get_device_info.return_value = None

        with pytest.raises(FailedDependency):
            self.broadcaster.consume_upstream()

        mock_api.stream_garage_door_events.assert_not_called()
