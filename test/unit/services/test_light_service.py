import datetime

from mock import patch, ANY
from werkzeug.exceptions import FailedDependency

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightAlarm
from svc.constants.settings_state import Settings
from svc.services.light_service import create_start_light_alarm


@patch('svc.services.light_service.LightState')
@patch('svc.services.light_service.UserDatabaseManager')
@patch('svc.services.light_service.get_light_api_key')
@patch('svc.services.light_service.create_thread')
class TestLightService:
    USER_NAME = 'test user'
    PASSWORD = 'test pass'
    USER_ID = 'def098'
    GROUP_ID = 'abc123'

    def setup_method(self):
        self.ALARM = LightAlarm(self.GROUP_ID, datetime.time(), 'MonTue')
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {"LightApiPass": self.PASSWORD, "LightApiUser": self.USER_NAME, 'UserId': self.USER_ID}

    def test_create_start_light_alarm__should_create_thread(self, mock_thread, mock_api, mock_db, mock_light):
        mock_light.get_instance.return_value.add_replace_light_alarm.return_value = self.ALARM
        create_start_light_alarm()

        mock_thread.assert_called_with(self.ALARM, ANY, Automation.TIME.TEN_SECONDS)

    def test_create_start_light_alarm__should_make_call_to_get_api_key(self, mock_thread, mock_api, mock_db, mock_light):
        create_start_light_alarm()

        mock_api.assert_called_with(self.USER_NAME, self.PASSWORD)

    def test_create_start_light_alarm__should_make_call_to_get_alarm_light_group(self, mock_thread, mock_api, mock_db, mock_light):
        create_start_light_alarm()

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called()

    def test_create_start_light_alarm__should_make_call_to_get_alarm_light_group_using_user_id_from_settings(self, mock_thread, mock_api, mock_db, mock_light):
        create_start_light_alarm()

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_create_start_light_alarm__should_create_light_state_object(self, mock_thread, mock_api, mock_db, mock_light):
        time = datetime.time()
        days = 'MonTueWed'
        group_id = 12
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = {'light_alarm': {'alarm_time': time, 'alarm_days': days, 'alarm_light_group': group_id}}
        create_start_light_alarm()

        mock_light.get_instance.return_value.add_replace_light_alarm.assert_called_with(group_id, time, days)

    def test_create_start_light_alarm__should_not_create_thread_when_alarm_time_is_none(self, mock_thread, mock_api, mock_db, mock_light):
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = {'city': 'Des Moines', 'light_alarm': {'alarm_time': None, 'alarm_days': 'montue'}}
        create_start_light_alarm()

        mock_thread.assert_not_called()

    def test_create_start_light_alarm__should_not_create_thread_when_alarm_is_none(self, mock_thread, mock_api, mock_db, mock_light):
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = {'city': 'Des Moines', 'light_alarm': {'alarm_time': datetime.time(), 'alarm_days': None}}
        create_start_light_alarm()

        mock_thread.assert_not_called()

    def test_create_start_light_alarm__should_return_none_when_api_key_raises_bad_dependency(self, mock_thread, mock_api, mock_db, mock_light):
        mock_api.side_effect = FailedDependency()
        actual = create_start_light_alarm()

        assert actual is None
