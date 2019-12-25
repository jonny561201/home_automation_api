from datetime import datetime

from mock import patch

from svc.constants.garage_state import GarageState
from svc.constants.home_automation import Automation
from svc.services.garage_door import monitor_status


@patch('svc.services.garage_door.datetime')
@patch('svc.services.garage_door.is_garage_open')
class TestGarageService:

    DATE = datetime.now()
    STATE = GarageState.get_instance()

    def test_monitor_status__should_set_status_to_open_when_garage_open(self, mock_status, mock_date):
        mock_status.return_value = True

        monitor_status()

        assert self.STATE.STATUS == Automation.GARAGE.OPEN

    def test_monitor_status__should_set_open_time_when_garage_open(self, mock_status, mock_date):
        mock_status.return_value = True
        mock_date.now.return_value = self.DATE

        monitor_status()

        assert self.STATE.OPEN_TIME == self.DATE

    def test_monitor_status__should_set_status_to_closed_when_garage_door_closed(self, mock_status, mock_date):
        mock_status.return_value = False

        monitor_status()

        assert self.STATE.STATUS == Automation.GARAGE.CLOSED

    def test_monitor_status__should_set_closed_time_when_garage_closed(self, mock_status, mock_date):
        mock_status.return_value = False
        mock_date.now.return_value = self.DATE

        monitor_status()

        assert self.STATE.CLOSED_TIME == self.DATE