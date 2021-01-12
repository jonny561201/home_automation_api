from threading import Event

from mock import patch, Mock, ANY

from svc.constants.home_automation import Automation
from svc.constants.hvac_state import HvacState
from svc.utilities.event_utils import create_thread


def test_function(*args):
    pass


@patch('svc.utilities.event_utils.MyThread')
@patch('svc.utilities.event_utils.Event')
class TestEvent:
    STATE = None
    FUNCT = test_function

    def setup_method(self):
        self.STATE = HvacState.get_instance()

    def test_create_thread__should_set_stop_event(self, mock_event, mock_thread):
        event = Event()
        mock_event.return_value = event
        create_thread(self.STATE, self.FUNCT)

        assert self.STATE.STOP_EVENT == event

    def test_create_thread__should_set_active_thread(self, mock_event, mock_thread):
        thread = Mock()
        mock_thread.return_value = thread
        create_thread(self.STATE, self.FUNCT)

        assert self.STATE.ACTIVE_THREAD == thread

    def test_create_thread__should_start_the_active_thread(self, mock_event, mock_thread):
        thread = Mock()
        mock_thread.return_value = thread
        create_thread(self.STATE, self.FUNCT)

        thread.start.assert_called()

    def test_create_thread__should_create_thread_with_stop_event(self, mock_event, mock_thread):
        event = Mock()
        mock_event.return_value = event
        create_thread(self.STATE, self.FUNCT)

        mock_thread.assert_called_with(event, ANY, ANY)

    def test_create_thread__should_create_thread_with_provided_function(self, mock_event, mock_thread):
        create_thread(self.STATE, self.FUNCT)

        mock_thread.assert_called_with(ANY, self.FUNCT, ANY)

    def test_create_thread__should_create_thread_with_default_delay(self, mock_event, mock_thread):
        create_thread(self.STATE, self.FUNCT)

        mock_thread.assert_called_with(ANY, ANY, Automation.TIME.THIRTY_SECONDS)

    def test_create_thread__should_create_thread_with_overridden_delay_value(self, mock_event, mock_thread):
        create_thread(self.STATE, self.FUNCT, Automation.TIME.TEN_MINUTE)

        mock_thread.assert_called_with(ANY, ANY, Automation.TIME.TEN_MINUTE)
