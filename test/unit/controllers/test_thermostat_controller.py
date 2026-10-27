import uuid

import jwt
import pytest
from mock import patch, ANY
from werkzeug.exceptions import NotFound

from svc.constants.home_automation import AuthClaims
from svc.constants.home_automation import Automation
from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature, get_user_forecast, get_user_extended_forecast
from svc.models.app import Preference, Task, Tasks
from svc.models.devices import DeviceInfo


@patch('svc.controllers.thermostat_controller.thermostat_service')
@patch('svc.controllers.thermostat_controller.api_utils')
@patch('svc.controllers.thermostat_controller.DeviceRepository')
@patch('svc.controllers.thermostat_controller.TasksRepository')
@patch('svc.controllers.thermostat_controller.UserRepository')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatTempController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    USER_ID = uuid.uuid4().hex
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    TIMEZONE_HEADER = 'America/Chicago'

    def setup_method(self):
        self.PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines')
        self.TASK = Task(alarmDays='Mon,Tue', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                         hvacStartTemp=68, hvacStopTemp=72, taskId='task-1', taskType='hvac',
                         hvacStart='06:00:00', hvacStop='08:00:00')
        self.TASKS = Tasks(tasks=[self.TASK])
        self.DEVICE_INFO = DeviceInfo(id='fake-device-id', ip_address='1.1.1.1', ip_port=5003, api_key='fake-api-key')
        self.STATUS = {'currentTemp': 20.0, 'desiredTemp': 21.0, 'mode': Automation.HVAC.MODE.HEATING}

    def __arrange(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        mock_device.return_value.__enter__.return_value.get_device_info.return_value = self.DEVICE_INFO
        mock_api.get_thermostat_status.return_value = self.STATUS

    def test_get_user_temp__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_temp__should_call_get_preferences_by_user(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_temp__should_load_hvac_tasks_for_user(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID, 'hvac')

    def test_get_user_temp__should_request_status_from_registered_thermostat(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_device.return_value.__enter__.return_value.get_device_info.assert_called_with('thermostat')
        mock_api.get_thermostat_status.assert_called_with('fake-api-key', 'http://1.1.1.1:5003')

    def test_get_user_temp__should_raise_not_found_when_thermostat_not_registered(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)
        mock_device.return_value.__enter__.return_value.get_device_info.side_effect = NotFound()

        with pytest.raises(NotFound):
            get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

    def test_get_user_temp__should_delegate_fahrenheit_temp_and_device_state_to_service(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_service.build_thermostat_state.assert_called_with(68.0, self.STATUS, True, self.TASKS.tasks, ANY)

    def test_get_user_temp__should_pass_celsius_temp_when_unit_is_celsius(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.PREFERENCE.tempUnit = 'celsius'
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_service.build_thermostat_state.assert_called_with(20.0, self.STATUS, False, self.TASKS.tasks, ANY)

    def test_get_user_temp__should_pass_none_temp_when_sensor_unavailable(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.STATUS['currentTemp'] = None
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_service.build_thermostat_state.assert_called_with(None, self.STATUS, True, self.TASKS.tasks, ANY)

    def test_get_user_temp__should_return_response_from_service(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)
        expected = object()
        mock_service.build_thermostat_state.return_value = expected

        actual = get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        assert actual is expected

    def test_get_user_temp__should_default_to_utc_when_header_missing(self, mock_jwt, mock_db, mock_tasks, mock_device, mock_api, mock_service):
        self.__arrange(mock_jwt, mock_db, mock_tasks, mock_device, mock_api)

        get_user_temp(self.JWT_TOKEN)

        args, _ = mock_service.build_thermostat_state.call_args
        assert str(args[4]) == 'UTC'


@patch('svc.controllers.thermostat_controller.thermostat_service')
@patch('svc.controllers.thermostat_controller.UserRepository')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatForecastController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    USER_ID = uuid.uuid4().hex
    CLAIMS = {AuthClaims.USER_ID: USER_ID}

    def setup_method(self):
        self.PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA')

    def test_get_user_forecast__should_validate_jwt_token(self, mock_jwt, mock_db, mock_service):
        get_user_forecast(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_forecast__should_get_the_preferences_by_user(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS

        get_user_forecast(self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_forecast__should_delegate_to_service_with_preference(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        get_user_forecast(self.JWT_TOKEN)

        mock_service.get_forecast_for_preference.assert_called_with(self.PREFERENCE)

    def test_get_user_forecast__should_return_response_from_service(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        response = {'myData': 'some value'}
        mock_service.get_forecast_for_preference.return_value = response

        actual = get_user_forecast(self.JWT_TOKEN)

        assert actual == response


@patch('svc.controllers.thermostat_controller.thermostat_service')
@patch('svc.controllers.thermostat_controller.UserRepository')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatExtendedForecastController:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    USER_ID = uuid.uuid4().hex
    CLAIMS = {AuthClaims.USER_ID: USER_ID}

    def setup_method(self):
        self.PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA')

    def test_get_user_extended_forecast__should_validate_jwt_token(self, mock_jwt, mock_db, mock_service):
        get_user_extended_forecast(self.JWT_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_extended_forecast__should_get_preferences_by_user(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS

        get_user_extended_forecast(self.JWT_TOKEN)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_extended_forecast__should_delegate_to_service_with_preference(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE

        get_user_extended_forecast(self.JWT_TOKEN, 'America/Chicago')

        mock_service.get_extended_forecast_for_preference.assert_called_with(self.PREFERENCE, ANY)

    def test_get_user_extended_forecast__should_return_response_from_service(self, mock_jwt, mock_db, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        response = {'forecast': []}
        mock_service.get_extended_forecast_for_preference.return_value = response

        actual = get_user_extended_forecast(self.JWT_TOKEN, 'America/Chicago')

        assert actual == response


@patch('svc.controllers.thermostat_controller.publish')
@patch('svc.controllers.thermostat_controller.convert_to_celsius')
@patch('svc.controllers.thermostat_controller.AuthClient')
class TestThermostatSetController:
    BEARER_TOKEN = 'fake bearer'
    DESIRED_CELSIUS_TEMP = 24.0
    DESIRED_FAHRENHEIT_TEMP = 68.9

    def setup_method(self):
        self.REQUEST = {'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': False, 'desiredTemp': self.DESIRED_CELSIUS_TEMP}

    def test_set_user_temperature__should_call_is_jwt_valid(self, mock_jwt, mock_convert, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_user_temperature__should_convert_fahrenheit_to_celsius(self, mock_jwt, mock_convert, mock_publish):
        request = {'mode': Automation.HVAC.MODE.COOLING, 'isFahrenheit': True, 'desiredTemp': self.DESIRED_FAHRENHEIT_TEMP}
        set_user_temperature(request, self.BEARER_TOKEN)

        mock_convert.assert_called_with(self.DESIRED_FAHRENHEIT_TEMP)

    def test_set_user_temperature__should_not_convert_celsius_request(self, mock_jwt, mock_convert, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_convert.assert_not_called()

    def test_set_user_temperature__should_publish_hvac_message(self, mock_jwt, mock_convert, mock_publish):
        set_user_temperature(self.REQUEST, self.BEARER_TOKEN)

        mock_publish.assert_called_with(Automation.HVAC.QUEUE, {'action': 'set', 'desiredTemp': self.DESIRED_CELSIUS_TEMP, 'mode': Automation.HVAC.MODE.HEATING})
