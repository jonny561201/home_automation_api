from mock import patch, ANY

from svc.constants.home_automation import HomeAutomation
from svc.utilities.hvac import run_temperature_program


@patch('svc.utilities.hvac.gpio')
@patch('svc.utilities.hvac.get_user_temperature')
@patch('svc.utilities.hvac.read_temperature_file')
class TestHvac:
    DESIRED_TEMP = 33.0
    AC_TEMP = 35.0
    HEAT_TEMP = 31.0

    def test_run_temperature_program__should_make_call_to_read_temperature_file(self, mock_temp, mock_convert, mock_gpio):
        run_temperature_program(self.DESIRED_TEMP)
        mock_temp.assert_called()

    def test_run_temperature_program__should_call_get_user_temperature(self, mock_temp, mock_convert, mock_gpio):
        mock_temp.return_value = self.AC_TEMP

        run_temperature_program(self.DESIRED_TEMP)
        mock_convert.assert_called()

    def test_run_temperature_program__should_make_call_to_get_user_temperature_with_result_of_temp_file(self, mock_temp, mock_convert, mock_gpio):
        mock_temp.return_value = self.AC_TEMP

        run_temperature_program(self.DESIRED_TEMP)
        mock_convert.assert_called_with(self.AC_TEMP, ANY)

    def test_run_temperature_program__should_make_call_to_get_user_temperature_with_celsius(self, mock_temp, mock_convert, mock_gpio):
        mock_temp.return_value = self.AC_TEMP

        run_temperature_program(self.DESIRED_TEMP)
        mock_convert.assert_called_with(ANY, False)

    def test_run_temperature_program__should_call_hvac_on_when_temp_above_desired(self, mock_temp, mock_convert, mock_gpio):
        mock_temp.return_value = self.AC_TEMP

        run_temperature_program(self.DESIRED_TEMP)
        mock_gpio.turn_on_hvac.assert_called()

    def test_run_temperature_program__should_turn_on_ac_when_temp_above_desired(self, mock_temp, mock_convert, mock_gpio):
        mock_temp.return_value = self.AC_TEMP

        run_temperature_program(self.DESIRED_TEMP)
        mock_gpio.turn_on_hvac.assert_called_with(HomeAutomation.AC)
