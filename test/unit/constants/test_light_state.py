import mock

from svc.constants.lights_state import LightState
from svc.constants.settings_state import Settings


@mock.patch('svc.constants.lights_state.get_light_api_key')
class TestLightState:
    API_KEY = 'abc123'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.STATE = LightState.get_instance()
        self.STATE.LIGHT_ALARMS = []

    def test_get_light_api_key__should_return_cached_api_key(self, mock_api):
        self.STATE.API_KEY = self.API_KEY
        actual = self.STATE.get_light_api_key()

        assert actual == self.API_KEY

    def test_get_light_api_key__should_make_call_to_get_key_when_not_cached(self, mock_api):
        self.STATE.API_KEY = None
        self.STATE.get_light_api_key()

        mock_api.assert_called_with(self.SETTINGS.light_api_user, self.SETTINGS.light_api_password)
