import datetime
from threading import Event

import mock

from svc.constants.lights_state import LightState, LightAlarm


class TestLightState:
    GROUP_ID = 4

    def setup_method(self):
        self.STATE = LightState.get_instance()
        self.STATE.LIGHT_ALARMS = []

    def test_add_light_alarm__should_create_new_light_alarm(self):
        self.STATE.add_light_alarm(datetime.time.fromisoformat('00:00:01'), 'Mon', self.GROUP_ID)
        assert len(self.STATE.LIGHT_ALARMS) == 1
        assert self.STATE.LIGHT_ALARMS[0].LIGHT_GROUP_ID == self.GROUP_ID

    def test_replace_light_alarm__should_cancel_existing_alarm(self):
        test_event = mock.create_autospec(Event)
        existing_alarm = LightAlarm(datetime.time.fromisoformat('00:00:01'), 'Mon')
        existing_alarm.STOP_EVENT = test_event
        existing_alarm.LIGHT_GROUP_ID = self.GROUP_ID
        self.STATE.LIGHT_ALARMS.append(existing_alarm)
        self.STATE.replace_light_alarm(self.GROUP_ID)

        assert len(self.STATE.LIGHT_ALARMS) == 1
        test_event.set.assert_called()