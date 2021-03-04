def read_temperature_file():
    return ['72 01 4b 46 7f ff 0e 10 57 : crc=57 YES',
            '72 01 4b 46 7f ff 0e 10 57 t=23125']
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read().split("\n")
    file_name = "/sys/bus/w1/devices/28-000006dfa76c/w1_slave"
