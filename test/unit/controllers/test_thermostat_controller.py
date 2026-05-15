import uuid

import jwt
from mock import patch, ANY

from svc.constants.home_automation import AuthClaims
from svc.constants.home_automation import Automation
from svc.controllers.thermostat_controller import get_user_temp, set_user_temperature, get_user_forecast, get_user_extended_forecast
from svc.models.app import Preference, Task, Tasks


@patch('svc.controllers.thermostat_controller.thermostat_service')
@patch('svc.controllers.thermostat_controller.read_temperature_file')
@patch('svc.controllers.thermostat_controller.get_user_temperature')
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

    def test_get_user_temp__should_call_is_jwt_valid(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.JWT_TOKEN)

    def test_get_user_temp__should_call_get_preferences_by_user(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_temp__should_load_hvac_tasks_for_user(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID, 'hvac')

    def test_get_user_temp__should_compute_internal_temp_from_temperature_file(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        temp_text = ['line1', 'line2']
        mock_file.return_value = temp_text

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_temp.assert_called_with(temp_text, True)

    def test_get_user_temp__should_delegate_to_service_with_internal_temp_and_fahrenheit_flag(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        mock_temp.return_value = 23.45

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_service.build_thermostat_state.assert_called_with(23.45, True, self.TASKS.tasks, ANY)

    def test_get_user_temp__should_pass_celsius_flag_when_unit_is_celsius(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        self.PREFERENCE.tempUnit = 'celsius'
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        mock_temp.return_value = 7.56

        get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        mock_service.build_thermostat_state.assert_called_with(7.56, False, self.TASKS.tasks, ANY)

    def test_get_user_temp__should_return_response_from_service(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS
        expected = object()
        mock_service.build_thermostat_state.return_value = expected

        actual = get_user_temp(self.JWT_TOKEN, self.TIMEZONE_HEADER)

        assert actual is expected

    def test_get_user_temp__should_default_to_utc_when_header_missing(self, mock_jwt, mock_db, mock_tasks, mock_temp, mock_file, mock_service):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.PREFERENCE
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = self.TASKS

        get_user_temp(self.JWT_TOKEN)

        args, _ = mock_service.build_thermostat_state.call_args
        assert str(args[3]) == 'UTC'


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
