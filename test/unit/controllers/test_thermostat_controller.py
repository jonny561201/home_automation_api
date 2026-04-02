import uuid

import jwt
from mock import patch, ANY

from svc.constants.home_automation import AuthClaims
from svc.constants.home_automation import Automation
from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature, get_user_forecast
from svc.models.app import Preference


@patch('svc.controllers.thermostat_controller.get_desired_temp')
@patch('svc.controllers.thermostat_controller.get_user_temperature')
@patch('svc.controllers.thermostat_controller.AccountRepository')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatTempController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    USER_ID = uuid.uuid4().hex
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56

    def setup_method(self):
        self.PREFERENCE = Preference(isFahrenheit=True, isImperial=True, tempUnit='Fahrenheit', city='Des Moines', garageId=1, garageDoor='Jons', measureUnit='in')

    def test_get_user_temp__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_temp, mock_file):
        get_user_temp(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_temp__should_call_get_preferences_by_user(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_user_temp(self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_temp__should_return_response_from_get_user_temp(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        expected_temp = 23.45
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_temp.return_value = expected_temp

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.currentTemp == expected_temp
        assert actual.isFahrenheit is True

    def test_get_user_temp__should_return_thermostat_temps_in_celsius(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        self.PREFERENCE.isFahrenheit = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.minThermostatTemp == 10.0
        assert actual.maxThermostatTemp == 32.0

    def test_get_user_temp__should_return_thermostat_temps_in_fahrenheit(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        self.PREFERENCE.isFahrenheit = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.minThermostatTemp == 50.0
        assert actual.maxThermostatTemp == 90.0

    def test_get_user_temp__should_return_the_hvac_mode(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        mock_file.return_value = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.mode == Automation.HVAC.MODE.HEATING

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_fahrenheit(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.COOLING}
        self.PREFERENCE.isFahrenheit = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_FAHR

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_celsius(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}
        self.PREFERENCE.isFahrenheit = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_CEL

    def test_get_user_temp__should_return_the_hvac_internal_temp_when_desired_temp_not_set(self, mock_jwt, mock_db, mock_temp, mock_file):
        mock_jwt.return_value = self.CLAIMS
        mock_file.return_value = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.HEATING}
        self.PREFERENCE.isFahrenheit = False
        mock_temp.return_value = self.TEMP_FAHR
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.JWT_TOKEN)

        assert actual.desiredTemp == self.TEMP_FAHR


@patch('svc.controllers.thermostat_controller.weather_request')
@patch('svc.controllers.thermostat_controller.AccountRepository')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatForecastController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    USER_ID = uuid.uuid4().hex
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56

    def setup_method(self):
        self.PREFERENCE = Preference(isFahrenheit=True, isImperial=True, tempUnit='Fahrenheit', city='Des Moines', garageId=1, garageDoor='Jons', measureUnit='in')

    def test_get_user_forecast__should_validate_jwt_token(self, mock_jwt, mock_db, mock_weather):
        get_user_forecast(self.JWT_TOKEN)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_forecast__should_get_the_preferences_by_user(self, mock_jwt, mock_db, mock_weather):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_user_forecast(self.JWT_TOKEN)
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_forecast__should_call_for_external_temp_with_preferences(self, mock_jwt, mock_db, mock_weather):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        get_user_forecast(self.JWT_TOKEN)
        mock_weather.get_weather.assert_called_with(self.PREFERENCE.city, self.PREFERENCE.tempUnit)

    def test_get_user_forecast__should_return_response_from_getting_external_temp(self, mock_jwt, mock_db, mock_weather):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        response = {'myData': 'some value'}
        mock_weather.get_weather.return_value = response
        actual = get_user_forecast(self.JWT_TOKEN)
        assert actual == response


@patch('svc.controllers.thermostat_controller.publish')
@patch('svc.controllers.thermostat_controller.write_desired_temp_to_file')
@patch('svc.controllers.thermostat_controller.convert_to_celsius')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatSetController:
    BEARER_TOKEN = 'fake bearer'
    DESIRED_CELSIUS_TEMP = 24.0
    DESIRED_FAHRENHEIT_TEMP = 68.9

    def setup_method(self):
        self.REQUEST = {'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': False, 'desiredTemp': self.DESIRED_CELSIUS_TEMP}

    def test_set_user_temperature__should_call_is_jwt_valid(self, mock_jwt, mock_convert, mock_file, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_user_temperature__should_convert_fahrenheit_to_celsius(self, mock_jwt, mock_convert, mock_file, mock_publish):
        request = {'mode': Automation.HVAC.MODE.COOLING, 'isFahrenheit': True, 'desiredTemp': self.DESIRED_FAHRENHEIT_TEMP}
        set_user_temperature(request, self.BEARER_TOKEN)

        mock_convert.assert_called_with(self.DESIRED_FAHRENHEIT_TEMP)

    def test_set_user_temperature__should_set_desired_temp(self, mock_jwt, mock_convert, mock_file, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_convert.assert_not_called()
        mock_file.assert_called_with(self.DESIRED_CELSIUS_TEMP, ANY)

    def test_set_user_temperature__should_set_mode(self, mock_jwt, mock_convert, mock_file, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_file.assert_called_with(ANY, Automation.HVAC.MODE.HEATING)

    def test_set_user_temperature__should_publish_hvac_message(self, mock_jwt, mock_convert, mock_file, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_publish.assert_called_with(Automation.HVAC.QUEUE, {'desiredTemp': self.DESIRED_CELSIUS_TEMP, 'mode': Automation.HVAC.MODE.HEATING, 'isAuto': False})
