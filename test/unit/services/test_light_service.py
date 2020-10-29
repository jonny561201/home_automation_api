from mock import patch, ANY

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightState
from svc.services.light_service import start_light_alarm


@patch('svc.services.light_service.create_thread')
class TestLightService:

    def setup_method(self):
        self.LIGHTS = LightState.get_instance()

    def test_start_light_alarm__should_create_thread(self, mock_thread):
        start_light_alarm()

        mock_thread.assert_called_with(self.LIGHTS, ANY, Automation.TIME.FIVE_SECONDS)
