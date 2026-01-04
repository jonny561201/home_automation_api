import json
import uuid

import jwt
from mock import patch, ANY

from svc.constants.home_automation import Automation
from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature, get_user_forecast


@patch('svc.controllers.thermostat_controller.get_desired_temp')
@patch('svc.controllers.thermostat_controller.temperature')
@patch('svc.controllers.thermostat_controller.UserDatabaseManager')
@patch('svc.controllers.thermostat_controller.is_jwt_valid')
class TestThermostatGetController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256').decode('UTF-8')
    USER_ID = uuid.uuid4().hex
    PREFERENCE = None
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56

    def setup_method(self):
        self.PREFERENCE = {'city': 'Des Moines', 'temp_unit': 'fahrenheit', 'is_fahrenheit': True}

    def test_get_user_temp__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_temp, mock_file):
        get_user_temp(self.USER_ID, self.JWT_TOKEN)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_temp__should_call_get_preferences_by_user(self, mock_jwt, mock_db, mock_temp, mock_file):
        get_user_temp(self.USER_ID, self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_temp__should_return_response_from_get_internal_temp(self, mock_jwt, mock_db, mock_temp, mock_file):
        expected_temp = 23.45
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_temp.get_internal_temp.return_value = expected_temp

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.currentTemp == expected_temp
        assert actual.isFahrenheit is True

    def test_get_user_temp__should_return_thermostat_temps_in_celsius(self, mock_jwt, mock_db, mock_temp, mock_file):
        self.PREFERENCE['is_fahrenheit'] = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.minThermostatTemp == 10.0
        assert actual.maxThermostatTemp == 32.0

    def test_get_user_temp__should_return_thermostat_temps_in_fahrenheit(self, mock_jwt, mock_db, mock_temp, mock_file):
        self.PREFERENCE['is_fahrenheit'] = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.minThermostatTemp == 50.0
        assert actual.maxThermostatTemp == 90.0

    def test_get_user_temp__should_return_the_hvac_mode(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_file.return_value = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.mode == Automation.HVAC.MODE.HEATING

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_fahrenheit(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.COOLING}
        self.PREFERENCE['is_fahrenheit'] = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_FAHR

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_celsius(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}
        self.PREFERENCE['is_fahrenheit'] = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_CEL

    def test_get_user_temp__should_return_the_hvac_internal_temp_when_desired_temp_not_set(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_file.return_value = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.HEATING}
        self.PREFERENCE['is_fahrenheit'] = False
        mock_temp.get_internal_temp.return_value = self.TEMP_FAHR
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_FAHR

    def test_get_user_forecast__should_validate_jwt_token(self, mock_jwt, mock_db, mock_temp, mock_file):
        get_user_forecast(self.USER_ID, self.JWT_TOKEN)
        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_forecast__should_get_the_preferences_by_user(self, mock_jwt, mock_db, mock_temp, mock_file):
        get_user_forecast(self.USER_ID, self.JWT_TOKEN)
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_forecast__should_call_for_external_temp_with_preferences(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        get_user_forecast(self.USER_ID, self.JWT_TOKEN)
        mock_temp.get_external_temp.assert_called_with(self.PREFERENCE)

    def test_get_user_forecast__should_return_response_from_getting_external_temp(self, mock_jwt, mock_db, mock_temp, mock_file):
        response = {'myData': 'some value'}
        mock_temp.get_external_temp.return_value = response
        actual = get_user_forecast(self.USER_ID, self.JWT_TOKEN)
        assert actual == response


@patch('svc.controllers.thermostat_controller.write_desired_temp_to_file')
@patch('svc.controllers.thermostat_controller.convert_to_celsius')
@patch('svc.controllers.thermostat_controller.is_jwt_valid')
class TestThermostatSetController:
    BEARER_TOKEN = 'fake bearer'
    DESIRED_CELSIUS_TEMP = 24.0
    DESIRED_FAHRENHEIT_TEMP = 68.9

    def setup_method(self):
        self.REQUEST = json.dumps({'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': False, 'desiredTemp': self.DESIRED_CELSIUS_TEMP}).encode('UTF-8')

    def test_set_user_temperature__should_call_is_jwt_valid(self, mock_jwt, mock_convert, mock_file):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_user_temperature__should_convert_fahrenheit_to_celsius(self, mock_jwt, mock_convert, mock_file):
        request = json.dumps({'mode': Automation.HVAC.MODE.COOLING, 'isFahrenheit': True, 'desiredTemp': self.DESIRED_FAHRENHEIT_TEMP}).encode('UTF-8')
        set_user_temperature(request, self.BEARER_TOKEN)

        mock_convert.assert_called_with(self.DESIRED_FAHRENHEIT_TEMP)

    def test_set_user_temperature__should_set_desired_temp(self, mock_jwt, mock_convert, mock_file):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_convert.assert_not_called()
        mock_file.assert_called_with(self.DESIRED_CELSIUS_TEMP, ANY)

    def test_set_user_temperature__should_set_mode(self, mock_jwt, mock_convert, mock_file):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_file.assert_called_with(ANY, Automation.HVAC.MODE.HEATING)
