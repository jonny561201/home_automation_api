import uuid
from datetime import datetime

from mock import patch

from svc.models.devices import DeviceInfo, NodeInfo
from svc.services.garage_status_service import build_user_doors


@patch('svc.services.garage_status_service.notify_garage_alert')
class TestBuildUserDoors:
    GARAGE_ID = '3'
    OTHER_GARAGE_ID = '99'
    DEVICE_ID = 'fake-device-id'
    IP_ADDRESS = '1.1.1.1'
    IP_PORT = 5000
    API_KEY = 'fake-api-key'
    DOOR_NAME = 'Left Garage'
    ALERT_TIME_MINUTES = 5

    def setup_method(self):
        self.NODE_ID = str(uuid.uuid4())
        self.DEVICE_INFO = DeviceInfo(id=self.DEVICE_ID, ip_address=self.IP_ADDRESS, ip_port=self.IP_PORT, api_key=self.API_KEY,
                                      nodes={self.GARAGE_ID: NodeInfo(name=self.DOOR_NAME, nodeId=self.NODE_ID)})

    def test_build_user_doors__should_keep_only_doors_in_user_nodes(self, mock_notify):
        doors = [
            {'garageId': self.GARAGE_ID, 'isGarageOpen': False, 'duration': '2025-01-01T00:00:00'},
            {'garageId': self.OTHER_GARAGE_ID, 'isGarageOpen': False, 'duration': '2025-01-01T00:00:00'},
        ]

        actual = build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        assert len(actual) == 1
        assert actual[0]['garageId'] == self.GARAGE_ID

    def test_build_user_doors__should_populate_door_name_and_node_id_from_device_info(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': False, 'duration': '2025-01-01T00:00:00'}]

        actual = build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        assert actual[0]['doorName'] == self.DOOR_NAME
        assert actual[0]['nodeId'] == self.NODE_ID

    def test_build_user_doors__should_flag_open_door_past_alert_time(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': True, 'duration': '2025-01-01T00:00:00'}]

        actual = build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        assert actual[0]['isPastAlertTime'] is True
        assert actual[0]['openTooLong'] is True

    def test_build_user_doors__should_not_flag_when_door_closed(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': False, 'duration': '2025-01-01T00:00:00'}]

        actual = build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        assert actual[0]['isPastAlertTime'] is False
        assert actual[0]['openTooLong'] is False

    def test_build_user_doors__should_not_flag_when_alert_time_zero(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': True, 'duration': '2025-01-01T00:00:00'}]

        actual = build_user_doors(doors, self.DEVICE_INFO, 0)

        assert actual[0]['isPastAlertTime'] is False
        assert actual[0]['openTooLong'] is False

    def test_build_user_doors__should_notify_when_door_past_alert_time(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': True, 'duration': '2025-01-01T00:00:00'}]

        build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        mock_notify.assert_called_with(self.DEVICE_ID, self.GARAGE_ID, self.DOOR_NAME, datetime.fromisoformat('2025-01-01T00:00:00'))

    def test_build_user_doors__should_not_notify_when_door_not_past_alert_time(self, mock_notify):
        doors = [{'garageId': self.GARAGE_ID, 'isGarageOpen': False, 'duration': '2025-01-01T00:00:00'}]

        build_user_doors(doors, self.DEVICE_INFO, self.ALERT_TIME_MINUTES)

        mock_notify.assert_not_called()
