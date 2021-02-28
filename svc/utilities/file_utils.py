import json

from svc.constants.settings_state import Settings


def write_status_to_file(door_number, time):
    file_name = Settings.get_instance().temp_file_name
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            content = json.load(file)
            content[door_number] = f'{time:%Y-%m-%d %H:%M:%S%z}'

        with open(file_name, "w") as file:
            json.dump(content, file)
    except FileNotFoundError:
        content = {door_number: f'{time:%Y-%m-%d %H:%M:%S%z}'}
        with open(file_name, "w+") as file:
            json.dump(content, file)
