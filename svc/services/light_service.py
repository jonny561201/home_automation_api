from svc.constants.home_automation import Automation
from svc.constants.lights_state import LightState
from svc.utilities.event_utils import create_thread
from svc.utilities.light_utils import run_light_program


def start_light_alarm():
    api_key = ''
    group_id = ''
    state = LightState.get_instance()
    if state.ALARM_THREAD is None:
        create_thread(state, lambda: run_light_program(api_key, group_id), Automation.TIME.FIVE_SECONDS)