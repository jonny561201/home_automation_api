import json

from svc.constants.home_automation import Automation
from svc.config.settings_state import Settings
from svc.utilities.file_utils import write_desired_temp_to_file


class TestFileUtils:
    FILE_NAME = 'test.json'

    def setup_method(self):
        settings = Settings.get_instance()
        settings._settings = {'TempFileName': self.FILE_NAME}

    def test_write_desired_temp_to_file__should_default_is_auto_to_false(self):
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING)
        with open(self.FILE_NAME) as file:
            content = json.load(file)
            assert content['isAuto'] is False

    def test_write_desired_temp_to_file__should_set_is_auto_to_true(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.AUTO)
        with open(file_name) as file:
            content = json.load(file)
            assert content['isAuto'] is True

    def test_write_desired_temp_to_file__should_save_mode(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.HEATING)
        with open(file_name) as file:
            content = json.load(file)
            assert content['mode'] == Automation.HVAC.MODE.HEATING

    def test_write_desired_temp_to_file__should_set_mode_to_auto_when_in_auto_mode(self):
        file_name = Settings.get_instance().temp_file_name
        write_desired_temp_to_file(12.2, Automation.HVAC.MODE.AUTO)
        with open(file_name) as file:
            content = json.load(file)
            assert content['mode'] == Automation.HVAC.MODE.AUTO
