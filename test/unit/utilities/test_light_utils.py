from datetime import datetime

from mock import patch

from svc.constants.lights_state import LightState
from svc.utilities.light_utils import run_light_program


@patch('svc.utilities.light_utils.set_light_groups')
class TestLightUtils:
    ALARM_TIME = datetime.now()
    API_KEY = 'test_api_key'
    GROUP_ID = '3'

    def setup_method(self):
        self.LIGHTS = LightState.get_instance()
        self.LIGHTS.ALARM_TIME = self.ALARM_TIME

    def test_run_light_program__should_call_set_light_group_if_after_start_time(self, mock_api):
        run_light_program(self.API_KEY, self.GROUP_ID)

        mock_api.assert_called_with(self.API_KEY, self.GROUP_ID, True, 1)
