import re
import os

import RPi.GPIO as GPIO
from glob import glob


THERMO_PIN = 11


GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(THERMO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_temperature_file():
    base_dir = '/sys/bus/w1/devices/'
    file_name = "w1_slave"
    try:
        device_folder = glob(base_dir + '28-*')[0]
        print(f'Temp Folder: {device_folder}')
        with open(os.path.join(device_folder, file_name), 'r', encoding='utf-8') as file:
            return file.read().split("\n")
    except Exception:
        return None


def get_user_temperature(temp_text, is_fahrenheit):
    if temp_text[0][-3:] != 'YES':
        return 0.0
    temp_string = re.search('(t=\d*)', temp_text[1])
    if temp_string is None:
        return 0.0

    celsius = _get_celsius_value(temp_string.group())
    return _convert_to_correct_unit(celsius, is_fahrenheit)


def convert_to_fahrenheit(celsius_temp):
    return celsius_temp * 1.8 + 32


def _get_celsius_value(temp_row):
    cleaned_text = temp_row.replace('t=', '')
    temp_celsius = int(cleaned_text)
    return round(temp_celsius / 1000, 2)


def _convert_to_correct_unit(celsius, is_fahrenheit):
    if is_fahrenheit:
        return convert_to_fahrenheit(celsius)
    return celsius


temp_file = read_temperature_file()
temp = get_user_temperature(temp_file, True)
print(f'Current Temp: {temp}')
