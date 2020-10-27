import datetime

from mock import patch

from svc.constants.lights_state import LightState
from svc.utilities.light_utils import run_light_program


@patch('svc.utilities.light_utils.set_light_groups')
class TestLightUtils:
    API_KEY = 'test_api_key'
    GROUP_ID = '3'

    def setup_method(self):
        self.ALARM_TIME = datetime.datetime.now()
        self.LIGHTS = LightState.get_instance()
        self.LIGHTS.ALARM_TIME = self.ALARM_TIME

    def test_run_light_program__should_call_set_light_group_if_after_start_time(self, mock_api):
        add_time = datetime.timedelta(minutes=1)
        self.LIGHTS.ALARM_TIME = self.ALARM_TIME + add_time
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)

    def test_run_light_program__should_not_call_set_light_group_if_before_start_time(self, mock_api):
        remove_time = datetime.timedelta(minutes=-1)
        self.LIGHTS.ALARM_TIME = self.ALARM_TIME + remove_time
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_not_called()
