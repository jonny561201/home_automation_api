import json
import os
import uuid

import jwt
from mock import patch

from svc.constants.home_automation import Automation
from svc.constants.hvac_state import HvacState
from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature
from svc.utilities.event_utils import MyThread
from svc.utilities.hvac_utils import run_temperature_program


@patch('svc.controllers.thermostat_controller.temperature')
@patch('svc.controllers.thermostat_controller.UserDatabaseManager')
@patch('svc.controllers.thermostat_controller.is_jwt_valid')
class TestThermostatGetController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256').decode('UTF-8')
    USER_ID = uuid.uuid4().hex
    PREFERENCE = None
    STATE = HvacState.get_instance()
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56

    def setup_method(self):
        self.STATE.DESIRED_TEMP = self.TEMP_FAHR
        self.PREFERENCE = {'city': 'Des Moines', 'temp_unit': 'fahrenheit', 'is_fahrenheit': True}

    def test_get_user_temp__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_temp):
        get_user_temp(self.USER_ID, self.JWT_TOKEN)

        mock_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_temp__should_call_get_preferences_by_user(self, mock_jwt, mock_db, mock_temp):
        get_user_temp(self.USER_ID, self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_temp__should_return_response_from_get_internal_temp(self, mock_jwt, mock_db, mock_temp):
        expected_temp = 23.45
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_temp.get_internal_temp.return_value = expected_temp

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['currentTemp'] == expected_temp
        assert actual['isFahrenheit'] is True

    def test_get_user_temp__should_consolidate_weather_response_with_get_external_temp(self, mock_jwt, mock_db, mock_temp):
        response = {'temp': 56.3, 'description': 'fake desc'}
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_temp.get_external_temp.return_value = response

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert response.items() <= actual.items()

    def test_get_user_temp__should_return_thermostat_temps_in_celsius(self, mock_jwt, mock_db, mock_temp):
        self.PREFERENCE['is_fahrenheit'] = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['minThermostatTemp'] == 10.0
        assert actual['maxThermostatTemp'] == 32.0

    def test_get_user_temp__should_return_thermostat_temps_in_fahrenheit(self, mock_jwt, mock_db, mock_temp):
        self.PREFERENCE['is_fahrenheit'] = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['minThermostatTemp'] == 50.0
        assert actual['maxThermostatTemp'] == 90.0

    def test_get_user_temp__should_return_the_hvac_mode(self, mock_jwt, mock_db, mock_temp):
        expected_mode = "heating"
        self.STATE.MODE = expected_mode

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['mode'] == expected_mode

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_fahrenheit(self, mock_jwt, mock_db, mock_temp):
        self.STATE.DESIRED_TEMP = self.TEMP_CEL
        self.STATE.IS_FAHRENHEIT = False
        self.PREFERENCE['is_fahrenheit'] = True
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['desiredTemp'] == self.TEMP_FAHR

    def test_get_user_temp__should_return_the_hvac_desired_temp_in_celsius(self, mock_jwt, mock_db, mock_temp):
        self.STATE.DESIRED_TEMP = self.TEMP_CEL
        self.PREFERENCE['is_fahrenheit'] = False
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['desiredTemp'] == self.TEMP_CEL

    def test_get_user_temp__should_return_the_hvac_internal_temp_when_desired_temp_not_set(self, mock_jwt, mock_db, mock_temp):
        self.STATE.DESIRED_TEMP = None
        self.PREFERENCE['is_fahrenheit'] = False
        mock_temp.get_internal_temp.return_value = self.TEMP_FAHR
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        actual = get_user_temp(self.USER_ID, self.JWT_TOKEN)

        assert actual['desiredTemp'] == self.TEMP_FAHR


@patch('svc.controllers.thermostat_controller.convert_to_celsius')
@patch('svc.controllers.thermostat_controller.is_jwt_valid')
class TestThermostatSetController:
    BEARER_TOKEN = 'fake bearer'
    DESIRED_CELSIUS_TEMP = 24.0
    DESIRED_FAHRENHEIT_TEMP = 68.9
    STATE = None

    def setup_method(self):
        self.STATE = HvacState.get_instance()
        self.STATE.ACTIVE_THREAD = MyThread(None, None, 0)
        self.REQUEST = json.dumps({'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': False, 'desiredTemp': self.DESIRED_CELSIUS_TEMP}).encode('UTF-8')

    def test_set_user_temperature__should_call_is_jwt_valid(self, mock_jwt, mock_convert):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_user_temperature__should_convert_fahrenheit_to_celsius(self, mock_jwt, mock_convert):
        request = json.dumps({'mode': Automation.HVAC.MODE.COOLING, 'isFahrenheit': True, 'desiredTemp': self.DESIRED_FAHRENHEIT_TEMP}).encode('UTF-8')
        set_user_temperature(request, self.BEARER_TOKEN)

        mock_convert.assert_called_with(self.DESIRED_FAHRENHEIT_TEMP)

    def test_set_user_temperature__should_set_desired_temp(self, mock_jwt, mock_convert):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        assert self.STATE.DESIRED_TEMP == self.DESIRED_CELSIUS_TEMP
        mock_convert.assert_not_called()

    @patch('svc.controllers.thermostat_controller.create_thread')
    def test_set_user_temperature__should_create_thread_when_none(self, mock_thread, mock_jwt, mock_convert):
        self.STATE.ACTIVE_THREAD = None
        self.STATE.STOP_EVENT = None
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_thread.assert_called_with(self.STATE, run_temperature_program)

    def test_set_user_temperature__should_set_mode(self, mock_jwt, mock_convert):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)
        assert self.STATE.MODE == Automation.HVAC.MODE.HEATING
