import datetime

from svc.constants.lights_state import LightState
from svc.utilities.api_utils import set_light_groups


def run_light_program(api_key, group_id):
    state = LightState.get_instance()
    now = datetime.datetime.now().time()
    if state.ALARM_START_TIME <= now < state.ALARM_STOP_TIME and state.ALARM_CURRENT_STATE < 255:
        state.ALARM_CURRENT_STATE += 1
        set_light_groups(api_key, group_id, True, state.ALARM_CURRENT_STATE)
    if state.ALARM_CURRENT_STATE != 0:
        state.ALARM_CURRENT_STATE = 0
