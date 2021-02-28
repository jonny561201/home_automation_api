import json

from werkzeug.exceptions import FailedDependency

from svc.constants.settings_state import Settings


def write_desired_temp_to_file(metric_temp, mode):
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = json.load(file)
            content['desiredTemp'] = metric_temp
            content['mode'] = mode

        with open(file_name, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        content = {'desiredTemp': metric_temp, 'mode': mode}
        with open(file_name, "w+") as file:
            json.dump(content, file)


def get_desired_temp():
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, TypeError):
        raise FailedDependency()
