from datetime import datetime

from svc.constants.lights_state import LightState
from svc.utilities.api_utils import set_light_groups


def run_light_program(api_key, group_id):
    # have a scheduled time of day to wake up by
    # check time of the day
    # 15 minutes prior to desired wake up time start process
    # every 17066 milliseconds we need to up the light group by one
    state = LightState.get_instance()
    now = datetime.now()
    if state.ALARM_TIME >= now:
        set_light_groups(api_key, group_id, True, 1)
