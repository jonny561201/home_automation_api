from mock import patch

from svc.constants.home_automation import Automation
from svc.models.app import Preference
from svc.services.thermostat_service import build_thermostat_state, get_forecast_for_preference, get_extended_forecast_for_preference


@patch('svc.services.thermostat_service.convert_to_fahrenheit')
@patch('svc.services.thermostat_service.get_desired_temp')
class TestBuildThermostatState:
    TEMP_FAHR = 45.608
    TEMP_CEL = 7.56
    INTERNAL_TEMP = 23.45

    def setup_method(self):
        self.STATE = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}

    def test_build_thermostat_state__should_return_current_temp(self, mock_file, mock_convert):
        mock_file.return_value = self.STATE

        actual = build_thermostat_state(self.INTERNAL_TEMP, True)

        assert actual.currentTemp == self.INTERNAL_TEMP

    def test_build_thermostat_state__should_return_is_fahrenheit_true(self, mock_file, mock_convert):
        mock_file.return_value = self.STATE

        actual = build_thermostat_state(self.INTERNAL_TEMP, True)

        assert actual.isFahrenheit is True

    def test_build_thermostat_state__should_return_is_fahrenheit_false(self, mock_file, mock_convert):
        mock_file.return_value = self.STATE

        actual = build_thermostat_state(self.INTERNAL_TEMP, False)

        assert actual.isFahrenheit is False

    def test_build_thermostat_state__should_return_none_current_temp_when_sensor_unavailable(self, mock_file, mock_convert):
        mock_file.return_value = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.TURN_OFF}

        actual = build_thermostat_state(None, True)

        assert actual.currentTemp is None
        assert actual.desiredTemp is None

    def test_build_thermostat_state__should_return_thermostat_temps_in_celsius(self, mock_file, mock_convert):
        mock_file.return_value = self.STATE

        actual = build_thermostat_state(self.INTERNAL_TEMP, False)

        assert actual.minThermostatTemp == 10.0
        assert actual.maxThermostatTemp == 32.0

    def test_build_thermostat_state__should_return_thermostat_temps_in_fahrenheit(self, mock_file, mock_convert):
        mock_file.return_value = self.STATE

        actual = build_thermostat_state(self.INTERNAL_TEMP, True)

        assert actual.minThermostatTemp == 50.0
        assert actual.maxThermostatTemp == 90.0

    def test_build_thermostat_state__should_return_the_hvac_mode(self, mock_file, mock_convert):
        mock_file.return_value = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}

        actual = build_thermostat_state(self.INTERNAL_TEMP, True)

        assert actual.mode == Automation.HVAC.MODE.HEATING

    def test_build_thermostat_state__should_return_the_hvac_desired_temp_in_fahrenheit(self, mock_file, mock_convert):
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.COOLING}
        mock_convert.return_value = self.TEMP_FAHR

        actual = build_thermostat_state(self.INTERNAL_TEMP, True)

        mock_convert.assert_called_with(self.TEMP_CEL)
        assert actual.desiredTemp == self.TEMP_FAHR

    def test_build_thermostat_state__should_return_the_hvac_desired_temp_in_celsius(self, mock_file, mock_convert):
        mock_file.return_value = {'desiredTemp': self.TEMP_CEL, 'mode': Automation.HVAC.MODE.HEATING}

        actual = build_thermostat_state(self.INTERNAL_TEMP, False)

        assert actual.desiredTemp == self.TEMP_CEL
        mock_convert.assert_not_called()

    def test_build_thermostat_state__should_return_the_internal_temp_when_desired_temp_not_set(self, mock_file, mock_convert):
        mock_file.return_value = {'desiredTemp': None, 'mode': Automation.HVAC.MODE.HEATING}

        actual = build_thermostat_state(self.TEMP_FAHR, False)

        assert actual.desiredTemp == self.TEMP_FAHR


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

    def setup_method(self):
        self.CITY_PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA')
        self.COORDS_PREFERENCE = Preference(
            tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA',
            latitude=self.LATITUDE, longitude=self.LONGITUDE,
        )

    def test_get_extended_forecast_for_preference__should_call_get_extended_weather_by_coords_when_coords_saved(self, mock_weather):
        get_extended_forecast_for_preference(self.COORDS_PREFERENCE)

        mock_weather.get_extended_weather_by_coords.assert_called_with(self.LATITUDE, self.LONGITUDE, self.COORDS_PREFERENCE.tempUnit)
        mock_weather.get_extended_weather_by_city.assert_not_called()

    def test_get_extended_forecast_for_preference__should_call_get_extended_weather_by_city_when_coords_missing(self, mock_weather):
        get_extended_forecast_for_preference(self.CITY_PREFERENCE)

        mock_weather.get_extended_weather_by_city.assert_called_with(self.CITY_PREFERENCE.city, self.CITY_PREFERENCE.tempUnit, self.CITY_PREFERENCE.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_fallback_to_city_when_only_latitude_saved(self, mock_weather):
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', latitude=self.LATITUDE)

        get_extended_forecast_for_preference(partial)

        mock_weather.get_extended_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_fallback_to_city_when_only_longitude_saved(self, mock_weather):
        partial = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Des Moines', state='IA', longitude=self.LONGITUDE)

        get_extended_forecast_for_preference(partial)

        mock_weather.get_extended_weather_by_city.assert_called_with(partial.city, partial.tempUnit, partial.state)
        mock_weather.get_extended_weather_by_coords.assert_not_called()

    def test_get_extended_forecast_for_preference__should_return_response_from_coords_path(self, mock_weather):
        response = {'forecast': []}
        mock_weather.get_extended_weather_by_coords.return_value = response

        actual = get_extended_forecast_for_preference(self.COORDS_PREFERENCE)

        assert actual == response

    def test_get_extended_forecast_for_preference__should_return_response_from_city_path(self, mock_weather):
        response = {'forecast': []}
        mock_weather.get_extended_weather_by_city.return_value = response

        actual = get_extended_forecast_for_preference(self.CITY_PREFERENCE)

        assert actual == response
