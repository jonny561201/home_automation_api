import json

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings
from svc.utilities.file_utils import write_desired_temp_to_file


def test_write_desired_temp_to_file__should_default_is_auto_to_false():
    file_name = Settings.get_instance().temp_file_name
    write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING)
    with open(file_name) as file:
        content = json.load(file)
        assert content['isAuto'] is False
