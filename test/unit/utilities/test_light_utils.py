import datetime

from mock import patch

from svc.constants.lights_state import LightAlarm
from svc.utilities.light_utils import run_light_program


@patch('svc.utilities.light_utils.datetime')
@patch('svc.utilities.light_utils.set_light_groups')
class TestLightUtils:
    API_KEY = 'test_api_key'
    GROUP_ID = '3'
    START_TIME = datetime.time(7, 30, 0)
    END_TIME = datetime.time(7, 40, 0)
    MONDAY = datetime.datetime(2020, 11, 2, 7, 34, 0)
    SUNDAY = datetime.datetime(2020, 11, 1, 7, 34, 0)
    WEDNESDAY = datetime.datetime(2020, 11, 4, 7, 34, 0)

    def setup_method(self):
        self.LIGHTS = LightAlarm(self.GROUP_ID, self.START_TIME, 'MonTueFri')
        self.LIGHTS.ALARM_COUNTER = 0
        self.LIGHTS.ALARM_START_TIME = self.START_TIME
        self.LIGHTS.ALARM_STOP_TIME = self.END_TIME

    def test_run_light_program__should_call_set_light_group_if_after_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = datetime.datetime(2020, 11, 2, 7, 31, 0)
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 2)

    def test_run_light_program__should_call_set_light_group_if_equal_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = datetime.datetime(2020, 11, 2, 7, 30, 0)
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 2)

    def test_run_light_program__should_not_call_set_light_group_if_before_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = datetime.datetime(2020, 11, 2, 7, 29, 0)
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_not_call_set_light_group_if_after_end_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = datetime.datetime(2020, 11, 2, 7, 41, 0)
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_increment_the_light_brightness(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = self.MONDAY
        self.LIGHTS.ALARM_COUNTER = 121
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 123)

    def test_run_light_program__should_reset_the_light_state_value_back_to_zero(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = datetime.datetime(2020, 11, 2, 7, 41, 0)
        self.LIGHTS.ALARM_CURRENT_STATE = 203
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
        assert self.LIGHTS.ALARM_COUNTER == 0

    def test_run_light_program__should_stop_incrementing_once_reach_255(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = self.MONDAY
        self.LIGHTS.ALARM_COUNTER = 255
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_not_call_set_light_group_when_sun(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = self.SUNDAY
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_not_call_set_light_group_when_wed(self, mock_api, mock_date):
        mock_date.datetime.now.return_value = self.WEDNESDAY
        run_light_program(self.LIGHTS, self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
