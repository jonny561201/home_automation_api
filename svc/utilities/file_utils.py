import json
import os
from glob import glob

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings


def write_desired_temp_to_file(metric_temp, mode):
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = json.load(file)
            content['desiredTemp'] = metric_temp
            content['mode'] = mode
            content['isAuto'] = mode == 'auto'

        with open(file_name, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        content = {'desiredTemp': metric_temp, 'mode': mode, 'isAuto': False}
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


def read_temperature_file():
    base_dir = '/sys/bus/w1/devices/'
    file_name = "w1_slave"
    try:
        device_folder = glob(base_dir + '28-*')[0]
        with open(os.path.join(device_folder, file_name), 'r', encoding='utf-8') as file:
            return file.read().split("\n")
    except Exception:
        return ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
                '72 01 4b 46 7f ff 0e 10 57 t=4078224']
