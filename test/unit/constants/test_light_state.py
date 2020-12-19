import datetime
from threading import Event

import mock

from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightState, LightAlarm
from svc.constants.settings_state import Settings


@mock.patch('svc.constants.lights_state.create_thread')
@mock.patch('svc.constants.lights_state.get_light_api_key')
class TestLightState:
    GROUP_ID = 4
    API_KEY = 'abc123'
    DAYS = 'MonTueWed'
    TIME = datetime.time.fromisoformat('00:00:01')

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.STATE = LightState.get_instance()
        self.STATE.LIGHT_ALARMS = []

    def test_add_replace_light_alarm__should_cancel_existing_alarm(self, mock_api, mock_thread):
        test_event = mock.create_autospec(Event)
        existing_alarm = LightAlarm(self.GROUP_ID, self.TIME, self.DAYS)
        existing_alarm.STOP_EVENT = test_event
        self.STATE.LIGHT_ALARMS.append(existing_alarm)
        self.STATE.add_replace_light_alarm(self.GROUP_ID, self.TIME, self.DAYS)

        assert len(self.STATE.LIGHT_ALARMS) == 1
        test_event.set.assert_called()

    def test_add_replace_light_alarm__should_create_a_new_alarm(self, mock_api, mock_thread):
        existing_alarm = LightAlarm(self.GROUP_ID, self.TIME, self.DAYS)
        existing_alarm.STOP_EVENT = mock.create_autospec(Event)
        self.STATE.LIGHT_ALARMS.append(existing_alarm)
        self.STATE.add_replace_light_alarm(self.GROUP_ID, self.TIME, self.DAYS)

        assert len(self.STATE.LIGHT_ALARMS) == 1
        assert self.STATE.LIGHT_ALARMS[0] != existing_alarm

    def test_add_replace_light_alarm__should_create_new_alarm_when_does_not_exist(self, mock_api, mock_thread):
        self.STATE.LIGHT_ALARMS.append(LightAlarm(55, self.TIME, self.DAYS))
        self.STATE.add_replace_light_alarm(self.GROUP_ID, self.TIME, self.DAYS)

        assert len(self.STATE.LIGHT_ALARMS) == 2

    def test_add_replace_light_alarm__should_return_the_created_light_alarm(self, mock_api, mock_thread):
        actual = self.STATE.add_replace_light_alarm(self.GROUP_ID, self.TIME, self.DAYS)

        assert actual is not None

    @mock.patch('svc.constants.lights_state.LightAlarm')
    def test_add_replace_light_alarm__should_create_the_light_thread(self, mock_light, mock_api, mock_thread):
        alarm = LightAlarm(self.GROUP_ID, self.TIME, self.DAYS)
        mock_light.return_value = alarm
        self.STATE.add_replace_light_alarm(self.GROUP_ID, self.TIME, self.DAYS)

        mock_thread.assert_called_with(alarm, mock.ANY, Automation.TIME.TEN_SECONDS)

    def test_get_light_api_key__should_return_cached_api_key(self, mock_api, mock_thread):
        self.STATE.API_KEY = self.API_KEY
        actual = self.STATE.get_light_api_key()

        assert actual == self.API_KEY

    def test_get_light_api_key__should_make_call_to_get_key_when_not_cached(self, mock_api, mock_thread):
        self.STATE.API_KEY = None
        self.STATE.get_light_api_key()

        mock_api.assert_called_with(self.SETTINGS.light_api_user, self.SETTINGS.light_api_password)

    def test_get_light_api_key__should_not_create_alarm_when_group_id_is_none(self, mock_api, mock_thread):
        self.STATE.add_replace_light_alarm(None, self.TIME, self.DAYS)

        assert len(self.STATE.LIGHT_ALARMS) == 0

    def test_get_light_api_key__should_not_create_alarm_when_alarm_time_is_none(self, mock_api, mock_thread):
        self.STATE.add_replace_light_alarm(self.GROUP_ID, None, self.DAYS)

        assert len(self.STATE.LIGHT_ALARMS) == 0
