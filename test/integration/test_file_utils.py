import json

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings
from svc.utilities.file_utils import write_desired_temp_to_file


class TestFileUtils:
    def setup_method(self):
        Settings.get_instance().dev_mode = True

    def test_write_desired_temp_to_file__should_default_is_auto_to_false(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING)
        with open(file_name) as file:
            content = json.load(file)
            assert content['isAuto'] is False

    def test_write_desired_temp_to_file__should_set_is_auto_to_true(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, None, True)
        with open(file_name) as file:
            content = json.load(file)
            assert content['isAuto'] is True

    def test_write_desired_temp_to_file__should_save_mode(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING, False)
        with open(file_name) as file:
            content = json.load(file)
            assert content['mode'] == Automation.HVAC.MODE.HEATING

    def test_write_desired_temp_to_file__should_set_mode_to_none_when_in_auto_mode(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING, True)
        with open(file_name) as file:
            content = json.load(file)
            assert content['mode'] is None
