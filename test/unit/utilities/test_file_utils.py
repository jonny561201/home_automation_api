from mock import patch, mock_open

from svc.constants.home_automation import Automation
from svc.utilities.file_utils import write_desired_temp_to_file, get_desired_temp, read_temperature_file


@patch('svc.utilities.file_utils.json')
@patch('svc.utilities.file_utils.Settings')
class TestWriteDesiredTempToFile:
    FILE_NAME = '/tmp/temperature.json'
    METRIC_TEMP = 22.22
    EXISTING_CONTENT = {'desiredTemp': 18.5, 'mode': 'cooling', 'isAuto': False}

    def test_write_desired_temp_to_file__should_update_existing_content_with_temp_and_mode(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        mock_json.load.return_value = dict(self.EXISTING_CONTENT)
        with patch('svc.utilities.file_utils.open', mock_open()):
            write_desired_temp_to_file(self.METRIC_TEMP, 'heating')

        written = mock_json.dump.call_args[0][0]
        assert written['desiredTemp'] == self.METRIC_TEMP
        assert written['mode'] == 'heating'
        assert written['isAuto'] is False

    def test_write_desired_temp_to_file__should_set_is_auto_true_when_mode_is_auto(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        mock_json.load.return_value = dict(self.EXISTING_CONTENT)
        with patch('svc.utilities.file_utils.open', mock_open()):
            write_desired_temp_to_file(self.METRIC_TEMP, 'auto')

        written = mock_json.dump.call_args[0][0]
        assert written['isAuto'] is True

    def test_write_desired_temp_to_file__should_create_default_content_when_file_not_found(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        m = mock_open()
        m.side_effect = [FileNotFoundError, m.return_value]
        with patch('svc.utilities.file_utils.open', m):
            write_desired_temp_to_file(self.METRIC_TEMP, 'heating')

        written = mock_json.dump.call_args[0][0]
        assert written == {'desiredTemp': self.METRIC_TEMP, 'mode': 'heating', 'isAuto': False}


@patch('svc.utilities.file_utils.json')
@patch('svc.utilities.file_utils.Settings')
class TestGetDesiredTemp:
    FILE_NAME = '/tmp/temperature.json'
    EXISTING_CONTENT = {'desiredTemp': 22.22, 'mode': 'heating', 'isAuto': False}

    def test_get_desired_temp__should_return_file_contents_when_file_exists(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        mock_json.load.return_value = dict(self.EXISTING_CONTENT)
        with patch('svc.utilities.file_utils.open', mock_open()):
            actual = get_desired_temp()

        assert actual == self.EXISTING_CONTENT

    def test_get_desired_temp__should_return_default_content_when_file_not_found(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        m = mock_open()
        m.side_effect = [FileNotFoundError, m.return_value]
        with patch('svc.utilities.file_utils.open', m):
            actual = get_desired_temp()

        assert actual == {'desiredTemp': 21.1111, 'mode': Automation.HVAC.MODE.TURN_OFF, 'isAuto': False}

    def test_get_desired_temp__should_write_default_content_when_file_not_found(self, mock_settings, mock_json):
        mock_settings.get_instance.return_value.temp_file_name = self.FILE_NAME
        m = mock_open()
        m.side_effect = [FileNotFoundError, m.return_value]
        with patch('svc.utilities.file_utils.open', m):
            get_desired_temp()

        written = mock_json.dump.call_args[0][0]
        assert written == {'desiredTemp': 21.1111, 'mode': Automation.HVAC.MODE.TURN_OFF, 'isAuto': False}


@patch('svc.utilities.file_utils.glob')
class TestReadTemperatureFile:
    DEVICE_FOLDER = '/sys/bus/w1/devices/28-abc'
    TEMP_LINE_1 = '72 01 4b 46 7f ff 0e 10 57 : crc=57 YES'
    TEMP_LINE_2 = '72 01 4b 46 7f ff 0e 10 57 t=23125'

    def test_read_temperature_file__should_return_file_content_split_by_newline(self, mock_glob):
        mock_glob.return_value = [self.DEVICE_FOLDER]
        contents = f'{self.TEMP_LINE_1}\n{self.TEMP_LINE_2}'
        with patch('svc.utilities.file_utils.open', mock_open(read_data=contents)):
            actual = read_temperature_file()

        assert actual == [self.TEMP_LINE_1, self.TEMP_LINE_2]

    def test_read_temperature_file__should_return_empty_list_when_no_device_folder_found(self, mock_glob):
        mock_glob.return_value = []

        actual = read_temperature_file()

        assert actual == []

    def test_read_temperature_file__should_return_empty_list_when_open_raises(self, mock_glob):
        mock_glob.return_value = [self.DEVICE_FOLDER]
        with patch('svc.utilities.file_utils.open', side_effect=OSError):
            actual = read_temperature_file()

        assert actual == []
