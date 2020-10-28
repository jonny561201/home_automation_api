import datetime

from mock import patch

from svc.constants.lights_state import LightState
from svc.utilities.light_utils import run_light_program


@patch('svc.utilities.light_utils.datetime')
@patch('svc.utilities.light_utils.set_light_groups')
class TestLightUtils:
    API_KEY = 'test_api_key'
    GROUP_ID = '3'

    def setup_method(self):
        self.ALARM_TIME = datetime.time(7, 30, 0)
        self.LIGHTS = LightState.get_instance()
        self.LIGHTS.ALARM_START_TIME = self.ALARM_TIME

    def test_run_light_program__should_call_set_light_group_if_after_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 31, 0)
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)

    def test_run_light_program__should_call_set_light_group_if_equal_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = self.ALARM_TIME
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)

    def test_run_light_program__should_not_call_set_light_group_if_before_start_time(self, mock_api, mock_date):
        mock_date.datetime.now.return_value.time.return_value = datetime.time(7, 29, 0)
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
