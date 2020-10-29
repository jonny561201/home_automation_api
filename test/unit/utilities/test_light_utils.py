import datetime

from mock import patch

from svc.constants.lights_state import LightState
from svc.utilities.light_utils import run_light_program


@patch('svc.utilities.light_utils.datetime')
@patch('svc.utilities.light_utils.set_light_groups')
class TestLightUtils:
    API_KEY = 'test_api_key'
    GROUP_ID = '3'
    START_TIME = datetime.time(7, 30, 0)
    END_TIME = datetime.time(7, 40, 0)

    def setup_method(self):
        self.LIGHTS = LightState.get_instance()
        self.LIGHTS.ALARM_CURRENT_STATE = 0
        self.LIGHTS.ALARM_START_TIME = self.START_TIME
        self.LIGHTS.ALARM_STOP_TIME = self.END_TIME

    def test_run_light_program__should_call_set_light_group_if_after_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 31, 0)
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)

    def test_run_light_program__should_call_set_light_group_if_equal_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = self.START_TIME
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)

    def test_run_light_program__should_not_call_set_light_group_if_before_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 29, 0)
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_not_call_set_light_group_if_after_end_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 41, 0)
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()

    def test_run_light_program__should_increment_the_light_brightness(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 34, 0)
        self.LIGHTS.ALARM_CURRENT_STATE = 121
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 122)

    def test_run_light_program__should_reset_the_light_state_value_back_to_zero(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 41, 0)
        self.LIGHTS.ALARM_CURRENT_STATE = 203
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
        assert self.LIGHTS.ALARM_CURRENT_STATE == 0

    def test_run_light_program__should_stop_incrementing_once_reach_255(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 34, 0)
        self.LIGHTS.ALARM_CURRENT_STATE = 255
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
