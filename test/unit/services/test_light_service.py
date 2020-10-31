from mock import patch, ANY

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightState
from svc.constants.settings_state import Settings
from svc.services.light_service import start_light_alarm


@patch('svc.services.light_service.UserDatabaseManager')
@patch('svc.services.light_service.get_light_api_key')
@patch('svc.services.light_service.create_thread')
class TestLightService:
    USER_NAME = 'test user'
    PASSWORD = 'test pass'
    USER_ID = 'def098'

    def setup_method(self):
        self.LIGHTS = LightState.get_instance()
        self.LIGHTS.ALARM_THREAD = None
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {"LightApiPass": self.PASSWORD, "LightApiUser": self.USER_NAME, 'UserId': self.USER_ID}

    def test_start_light_alarm__should_create_thread(self, mock_thread, mock_api, mock_db):
        start_light_alarm()

        mock_thread.assert_called_with(self.LIGHTS, ANY, Automation.TIME.TEN_SECONDS)

    def test_start_light_alarm__should_make_call_to_get_api_key(self, mock_thread, mock_api, mock_db):
        start_light_alarm()

        mock_api.assert_called_with(self.USER_NAME, self.PASSWORD)

    def test_start_light_alarm__should_not_make_api_call_when_thread_already_created(self, mock_thread, mock_api, mock_db):
        self.LIGHTS.ALARM_THREAD = {}
        start_light_alarm()

        mock_api.assert_not_called()

    def test_start_light_alarm__should_make_call_to_get_alarm_light_group(self, mock_thread, mock_api, mock_db):
        start_light_alarm()

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called()

    def test_start_light_alarm__should_make_call_to_get_alarm_light_group_using_user_id_from_settings(self, mock_thread, mock_api, mock_db):
        start_light_alarm()

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)
