import datetime

from svc.constants.lights_state import LightState


def test_add_light_alarm__should_create_new_light_alarm():
    state = LightState.get_instance()
    group_id = 4
    state.add_light_alarm(datetime.time.fromisoformat('00:00:01'), 'Mon', group_id)
    assert len(state.LIGHT_ALARMS) == 1
    assert state.LIGHT_ALARMS[0].LIGHT_GROUP_ID == group_id

    