import json

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings


def write_desired_temp_to_file(metric_temp, mode, isAuto=False):
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = json.load(file)
            content['desiredTemp'] = metric_temp
            content['mode'] = mode
            content['isAuto'] = isAuto

        with open(file_name, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        content = {'desiredTemp': metric_temp, 'mode': mode, 'isAuto': isAuto}
        with open(file_name, "w+") as file:
            json.dump(content, file)


def get_desired_temp():
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, TypeError):
        content = {'desiredTemp': 21.1111, 'mode': Automation.HVAC.MODE.TURN_OFF, 'isAuto': False}
        with open(file_name, "w+") as file:
            json.dump(content, file)
        return content

