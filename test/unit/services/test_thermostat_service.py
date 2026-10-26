from datetime import datetime
from zoneinfo import ZoneInfo

from mock import patch

from svc.constants.home_automation import Automation
from svc.models.app import Preference, Task
from svc.models.thermostat import ExtendedForecast, ForecastDay
from svc.services.thermostat_service import build_thermostat_state, get_forecast_for_preference, get_extended_forecast_for_preference


@patch('svc.services.thermostat_service.now_in_timezone')
@patch('svc.services.thermostat_service.convert_to_fahrenheit')
class TestBuildThermostatState:
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56
    INTERNAL_TEMP = 23.45
    TZ = ZoneInfo('UTC')

    def setup_method(self):
        self.STATE = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}
        self.NOW_LOCAL = datetime(2026, 5, 11, 12, 0, tzinfo=self.TZ)

    def test_build_thermostat_state__should_return_current_temp(self, mock_convert, mock_now):
        state = self.STATE
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.currentTemp == self.INTERNAL_TEMP

    def test_build_thermostat_state__should_return_is_fahrenheit_true(self, mock_convert, mock_now):
        state = self.STATE
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.isFahrenheit is True

    def test_build_thermostat_state__should_return_is_fahrenheit_false(self, mock_convert, mock_now):
        state = self.STATE
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, False, [], self.TZ)

        assert actual.isFahrenheit is False

    def test_build_thermostat_state__should_return_none_current_temp_when_sensor_unavailable(self, mock_convert, mock_now):
        state = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.TURN_OFF}
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(None, state, True, [], self.TZ)

        assert actual.currentTemp is None
        assert actual.desiredTemp is None

    def test_build_thermostat_state__should_return_thermostat_temps_in_celsius(self, mock_convert, mock_now):
        state = self.STATE
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, False, [], self.TZ)

        assert actual.minThermostatTemp == 10.0
        assert actual.maxThermostatTemp == 32.0

    def test_build_thermostat_state__should_return_thermostat_temps_in_fahrenheit(self, mock_convert, mock_now):
        state = self.STATE
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.minThermostatTemp == 50.0
        assert actual.maxThermostatTemp == 90.0

    def test_build_thermostat_state__should_return_the_hvac_mode(self, mock_convert, mock_now):
        state = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.mode == Automation.HVAC.MODE.HEATING

    def test_build_thermostat_state__should_return_the_hvac_desired_temp_in_fahrenheit(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.COOLING}
        mock_convert.return_value = self.TEMP_FAHR
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        mock_convert.assert_called_with(self.TEMP_CEL)
        assert actual.desiredTemp == self.TEMP_FAHR

    def test_build_thermostat_state__should_return_the_hvac_desired_temp_in_celsius(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, False, [], self.TZ)

        assert actual.desiredTemp == self.TEMP_CEL
        mock_convert.assert_not_called()

    def test_build_thermostat_state__should_return_the_internal_temp_when_desired_temp_not_set(self, mock_convert, mock_now):
        state = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.HEATING}
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.TEMP_FAHR, state, False, [], self.TZ)

        assert actual.desiredTemp == self.TEMP_FAHR

    def test_build_thermostat_state__should_return_active_task_when_now_inside_window(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 7, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon,Tue', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.activeTask is not None
        assert actual.activeTask.startTemp == 68
        assert actual.activeTask.stopTemp == 72
        assert actual.activeTask.stop == '08:00'

    def test_build_thermostat_state__should_return_null_active_task_when_no_match(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 9, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.activeTask is None

    def test_build_thermostat_state__should_skip_disabled_tasks_when_computing_active(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 7, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon', alarmGroupName='', alarmLightGroup='', enabled=False, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.activeTask is None

    def test_build_thermostat_state__should_return_next_task_today_when_later_today(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 5, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.nextTask is not None
        assert actual.nextTask.startTemp == 68
        assert actual.nextTask.start == '06:00'
        assert actual.nextTask.dayLabel == 'Today'

    def test_build_thermostat_state__should_return_next_task_future_day(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 9, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Wed', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.nextTask is not None
        assert actual.nextTask.dayLabel == 'Wed'

    def test_build_thermostat_state__should_return_null_next_task_when_none_match(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 9, 0, tzinfo=self.TZ)

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.nextTask is None

    def test_build_thermostat_state__should_set_current_desired_temp_to_active_start_temp(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 7, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.currentDesiredTemp == 68

    def test_build_thermostat_state__should_set_current_desired_temp_to_first_stop_temp_when_no_active_task(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 9, 0, tzinfo=self.TZ)
        task = Task(alarmDays='Mon', alarmGroupName='', alarmLightGroup='', enabled=True, hvacMode='heating',
                    hvacStartTemp=68, hvacStopTemp=72, taskId='t1', taskType='hvac',
                    hvacStart='06:00:00', hvacStop='08:00:00')

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [task], self.TZ)

        assert actual.currentDesiredTemp == 72

    def test_build_thermostat_state__should_set_current_desired_temp_to_midpoint_when_no_matching_tasks_today(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.AUTO}
        mock_now.return_value = datetime(2026, 5, 11, 9, 0, tzinfo=self.TZ)

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, True, [], self.TZ)

        assert actual.currentDesiredTemp == 70.0

    def test_build_thermostat_state__should_set_current_desired_temp_to_desired_temp_when_mode_not_auto(self, mock_convert, mock_now):
        state = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}
        mock_now.return_value = self.NOW_LOCAL

        actual = build_thermostat_state(self.INTERNAL_TEMP, state, False, [], self.TZ)

        assert actual.currentDesiredTemp == self.TEMP_CEL


@patch('svc.services.thermostat_service.weather_request')
class TestGetForecastForPreference:
    LATITUDE = 41.5868
    LONGITUDE = -93.625

    def setup_method(self):
        self.CITY_PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA')
        self.COORDS_PREFERENCE = Preference(
            tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA',
            latitude=self.LATITUDE, longitude=self.LONGITUDE,
        )

    def test_get_forecast_for_preference__should_call_get_weather_by_coords_when_coords_saved(self, mock_weather):
        get_forecast_for_preference(self.COORDS_PREFERENCE)

        mock_weather.get_weather_by_coords.assert_called_with(self.LATITUDE, self.LONGITUDE, self.COORDS_PREFERENCE.tempUnit)
        mock_weather.get_weather_by_city.assert_not_called()

    def test_get_forecast_for_preference__should_call_get_weather_by_city_when_coords_missing(self, mock_weather):
        get_forecast_for_preference(self.CITY_PREFERENCE)

        mock_weather.get_weather_by_city.assert_called_with(self.CITY_PREFERENCE.city, self.CITY_PREFERENCE.tempUnit, self.CITY_PREFERENCE.state)
        mock_weather.get_weather_by_coords.assert_not_called()

    def test_get_forecast_for_preference__should_fallback_to_city_when_only_latitude_saved(self, mock_weather):
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', latitude=self.LATITUDE)

        get_forecast_for_preference(partial)

        mock_weather.get_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_weather_by_coords.assert_not_called()

    def test_get_forecast_for_preference__should_fallback_to_city_when_only_longitude_saved(self, mock_weather):
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', longitude=self.LONGITUDE)

        get_forecast_for_preference(partial)

        mock_weather.get_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_weather_by_coords.assert_not_called()

    def test_get_forecast_for_preference__should_return_response_from_coords_path(self, mock_weather):
        response = {'myData': 'some value'}
        mock_weather.get_weather_by_coords.return_value = response

        actual = get_forecast_for_preference(self.COORDS_PREFERENCE)

        assert actual == response

    def test_get_forecast_for_preference__should_return_response_from_city_path(self, mock_weather):
        response = {'myData': 'some value'}
        mock_weather.get_weather_by_city.return_value = response

        actual = get_forecast_for_preference(self.CITY_PREFERENCE)

        assert actual == response


@patch('svc.services.thermostat_service.weather_request')
class TestGetExtendedForecastForPreference:
    LATITUDE = 41.5868
    LONGITUDE = -93.625
    TZ = ZoneInfo('UTC')

    def setup_method(self):
        self.CITY_PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA')
        self.COORDS_PREFERENCE = Preference(
            tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA',
            latitude=self.LATITUDE, longitude=self.LONGITUDE,
        )
        self.FORECAST = ExtendedForecast(forecast=[
            ForecastDay(date='2026-05-11', minTemp=49.6, maxTemp=72.3, description='Sunny'),
            ForecastDay(date='2026-05-12', minTemp=52.1, maxTemp=68.9, description='Cloudy'),
        ])

    def test_get_extended_forecast_for_preference__should_call_get_extended_weather_by_coords_when_coords_saved(self, mock_weather):
        mock_weather.get_extended_weather_by_coords.return_value = self.FORECAST
        get_extended_forecast_for_preference(self.COORDS_PREFERENCE, self.TZ)

        mock_weather.get_extended_weather_by_coords.assert_called_with(self.LATITUDE, self.LONGITUDE, self.COORDS_PREFERENCE.tempUnit)
        mock_weather.get_extended_weather_by_city.assert_not_called()

    def test_get_extended_forecast_for_preference__should_call_get_extended_weather_by_city_when_coords_missing(self, mock_weather):
        mock_weather.get_extended_weather_by_city.return_value = self.FORECAST
        get_extended_forecast_for_preference(self.CITY_PREFERENCE, self.TZ)

        mock_weather.get_extended_weather_by_city.assert_called_with(self.CITY_PREFERENCE.city, self.CITY_PREFERENCE.tempUnit, self.CITY_PREFERENCE.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_fallback_to_city_when_only_latitude_saved(self, mock_weather):
        mock_weather.get_extended_weather_by_city.return_value = self.FORECAST
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', latitude=self.LATITUDE)

        get_extended_forecast_for_preference(partial, self.TZ)

        mock_weather.get_extended_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_fallback_to_city_when_only_longitude_saved(self, mock_weather):
        mock_weather.get_extended_weather_by_city.return_value = self.FORECAST
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', longitude=self.LONGITUDE)

        get_extended_forecast_for_preference(partial, self.TZ)

        mock_weather.get_extended_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_return_response_with_day_label(self, mock_weather):
        mock_weather.get_extended_weather_by_coords.return_value = self.FORECAST

        actual = get_extended_forecast_for_preference(self.COORDS_PREFERENCE, self.TZ)

        assert actual.forecast[0].day == 'Mon'
        assert actual.forecast[1].day == 'Tue'

    def test_get_extended_forecast_for_preference__should_round_temps_to_int(self, mock_weather):
        mock_weather.get_extended_weather_by_coords.return_value = self.FORECAST

        actual = get_extended_forecast_for_preference(self.COORDS_PREFERENCE, self.TZ)

        assert actual.forecast[0].high == 72
        assert actual.forecast[0].low == 50
        assert actual.forecast[1].high == 69
        assert actual.forecast[1].low == 52
