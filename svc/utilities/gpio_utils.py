from glob import glob
import os


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
