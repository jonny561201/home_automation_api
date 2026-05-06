from mock import patch
from requests.exceptions import ConnectionError

from svc.services.weather_request import (get_weather_by_coords, get_weather_by_city,
                                           get_extended_weather_by_coords, get_extended_weather_by_city)


@patch('svc.services.weather_request.get_forecast_by_coords')
class TestGetWeatherByCoords:
    LATITUDE = 41.5868
    LONGITUDE = -93.625
    UNIT = 'fahrenheit'

    def setup_method(self):
        self.DAY = {'temperature_2m_min': [12.34], 'temperature_2m_max': [12.87]}
        self.TEMP = {'temperature': 64.8, 'weathercode': 2}
        self.FORECAST_RESPONSE = {'daily': self.DAY, 'current_weather': self.TEMP}

    def test_get_weather_by_coords__should_call_forecast_with_lat_lon_and_unit(self, mock_forecast):
        mock_forecast.return_value = self.FORECAST_RESPONSE
        get_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        mock_forecast.assert_called_with(self.LATITUDE, self.LONGITUDE, self.UNIT)

    def test_get_weather_by_coords__should_return_temp_data(self, mock_forecast):
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.temp == self.TEMP['temperature']

    def test_get_weather_by_coords__should_return_min_and_max_temp(self, mock_forecast):
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.minTemp == self.DAY['temperature_2m_min'][0]
        assert actual.maxTemp == self.DAY['temperature_2m_max'][0]

    def test_get_weather_by_coords__should_return_weather_description(self, mock_forecast):
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.description == 'partly cloudy'

    def test_get_weather_by_coords__should_return_default_values_on_connection_error(self, mock_forecast):
        mock_forecast.side_effect = ConnectionError()
        actual = get_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.temp == 0.0
        assert actual.minTemp == 0.0
        assert actual.maxTemp == 0.0
        assert actual.description == 'sunny'


@patch('svc.services.weather_request.get_forecast_by_coords')
@patch('svc.services.weather_request.get_city_coordinates')
class TestGetWeatherByCity:
    CITY = 'Prague'
    STATE = 'IA'
    UNIT = 'metric'
    COORDS = {'latitude': 92.00, 'longitude': -93.85}

    def setup_method(self):
        self.DAY = {'temperature_2m_min': [12.34], 'temperature_2m_max': [12.87]}
        self.TEMP = {'temperature': 64.8, 'weathercode': 2}
        self.CITY_RESPONSE = {'results': [self.COORDS]}
        self.FORECAST_RESPONSE = {'daily': self.DAY, 'current_weather': self.TEMP}

    def test_get_weather_by_city__should_call_geocode_with_city_and_state(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        get_weather_by_city(self.CITY, self.UNIT, self.STATE)
        mock_city.assert_called_with(self.CITY, self.STATE)

    def test_get_weather_by_city__should_default_state_to_none(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        get_weather_by_city(self.CITY, self.UNIT)
        mock_city.assert_called_with(self.CITY, None)

    def test_get_weather_by_city__should_call_forecast_using_geocoded_coords(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        get_weather_by_city(self.CITY, self.UNIT, self.STATE)
        mock_forecast.assert_called_with(self.COORDS['latitude'], self.COORDS['longitude'], self.UNIT)

    def test_get_weather_by_city__should_return_temp_data(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.temp == self.TEMP['temperature']

    def test_get_weather_by_city__should_return_min_and_max_temp(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.minTemp == self.DAY['temperature_2m_min'][0]
        assert actual.maxTemp == self.DAY['temperature_2m_max'][0]

    def test_get_weather_by_city__should_return_weather_description(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.description == 'partly cloudy'

    def test_get_weather_by_city__should_return_defaults_when_geocode_returns_no_results(self, mock_city, mock_forecast):
        mock_city.return_value = {}
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.temp == 0.0
        assert actual.minTemp == 0.0
        assert actual.maxTemp == 0.0
        assert actual.description == 'sunny'
        mock_forecast.assert_not_called()

    def test_get_weather_by_city__should_return_defaults_on_geocode_connection_error(self, mock_city, mock_forecast):
        mock_city.side_effect = ConnectionError()
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.temp == 0.0
        assert actual.description == 'sunny'
        mock_forecast.assert_not_called()

    def test_get_weather_by_city__should_return_defaults_on_forecast_connection_error(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.side_effect = ConnectionError()
        actual = get_weather_by_city(self.CITY, self.UNIT)
        assert actual.temp == 0.0
        assert actual.description == 'sunny'


@patch('svc.services.weather_request.get_extended_forecast_by_coords')
class TestGetExtendedWeatherByCoords:
    LATITUDE = 41.5868
    LONGITUDE = -93.625
    UNIT = 'fahrenheit'

    def setup_method(self):
        self.PAYLOAD = {
            'daily': {
                'time': ['2026-05-06', '2026-05-07', '2026-05-08'],
                'temperature_2m_min': [50.0, 52.0, 48.0],
                'temperature_2m_max': [70.0, 72.0, 68.0],
                'weathercode': [0, 2, 61],
            }
        }

    def test_get_extended_weather_by_coords__should_call_api_with_default_days(self, mock_forecast):
        mock_forecast.return_value = self.PAYLOAD
        get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        mock_forecast.assert_called_with(self.LATITUDE, self.LONGITUDE, self.UNIT, 5)

    def test_get_extended_weather_by_coords__should_return_one_forecast_per_day(self, mock_forecast):
        mock_forecast.return_value = self.PAYLOAD
        actual = get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert len(actual.forecast) == 3

    def test_get_extended_weather_by_coords__should_map_each_day_fields(self, mock_forecast):
        mock_forecast.return_value = self.PAYLOAD
        actual = get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        first = actual.forecast[0]
        assert first.date == '2026-05-06'
        assert first.minTemp == 50.0
        assert first.maxTemp == 70.0
        assert first.description == 'sunny'

    def test_get_extended_weather_by_coords__should_translate_weather_code_to_description(self, mock_forecast):
        mock_forecast.return_value = self.PAYLOAD
        actual = get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.forecast[1].description == 'partly cloudy'

    def test_get_extended_weather_by_coords__should_return_empty_on_connection_error(self, mock_forecast):
        mock_forecast.side_effect = ConnectionError()
        actual = get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.forecast == []

    def test_get_extended_weather_by_coords__should_return_empty_when_payload_missing_daily(self, mock_forecast):
        mock_forecast.return_value = {}
        actual = get_extended_weather_by_coords(self.LATITUDE, self.LONGITUDE, self.UNIT)
        assert actual.forecast == []


@patch('svc.services.weather_request.get_extended_forecast_by_coords')
@patch('svc.services.weather_request.get_city_coordinates')
class TestGetExtendedWeatherByCity:
    CITY = 'Prague'
    STATE = 'IA'
    UNIT = 'metric'
    COORDS = {'latitude': 41.0, 'longitude': -93.0}

    def setup_method(self):
        self.CITY_RESPONSE = {'results': [self.COORDS]}
        self.PAYLOAD = {
            'daily': {
                'time': ['2026-05-06'],
                'temperature_2m_min': [10.0],
                'temperature_2m_max': [20.0],
                'weathercode': [0],
            }
        }

    def test_get_extended_weather_by_city__should_geocode_city_and_state(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.PAYLOAD
        get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        mock_city.assert_called_with(self.CITY, self.STATE)

    def test_get_extended_weather_by_city__should_call_forecast_with_geocoded_coords_and_default_days(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.PAYLOAD
        get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        mock_forecast.assert_called_with(self.COORDS['latitude'], self.COORDS['longitude'], self.UNIT, 5)

    def test_get_extended_weather_by_city__should_return_forecast_days(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.PAYLOAD
        actual = get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        assert len(actual.forecast) == 1
        assert actual.forecast[0].date == '2026-05-06'

    def test_get_extended_weather_by_city__should_return_empty_when_geocode_returns_no_results(self, mock_city, mock_forecast):
        mock_city.return_value = {}
        actual = get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        assert actual.forecast == []
        mock_forecast.assert_not_called()

    def test_get_extended_weather_by_city__should_return_empty_on_geocode_connection_error(self, mock_city, mock_forecast):
        mock_city.side_effect = ConnectionError()
        actual = get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        assert actual.forecast == []
        mock_forecast.assert_not_called()

    def test_get_extended_weather_by_city__should_return_empty_on_forecast_connection_error(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.side_effect = ConnectionError()
        actual = get_extended_weather_by_city(self.CITY, self.UNIT, self.STATE)
        assert actual.forecast == []
