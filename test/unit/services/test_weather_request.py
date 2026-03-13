from mock import patch
from requests.exceptions import ConnectionError

from svc.services.weather_request import get_weather


@patch('svc.services.weather_request.get_forecast_by_coords')
@patch('svc.services.weather_request.get_city_coordinates')
class TestWeatherRequest:
    CITY = 'Prague'
    UNIT = 'metric'
    COORDS = {'latitude': 92.00, 'longitude': -93.85}

    def setup_method(self):
        self.DAY = {'temperature_2m_min': [12.34], 'temperature_2m_max': [12.87]}
        self.TEMP = {'temperature': 64.8, 'weathercode': 2}
        self.CITY_RESPONSE = {'results': [self.COORDS]}
        self.FORECAST_RESPONSE = {'daily': self.DAY, 'current_weather': self.TEMP}

    def test_get_weather__should_return_temp_data(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.temp == self.TEMP['temperature']

    def test_get_weather__should_return_default_temp_value_of_zero(self, mock_city, mock_forecast):
        self.TEMP = {'weathercode': 0}
        self.FORECAST_RESPONSE = {'daily': self.DAY, 'current_weather': self.TEMP}
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.temp == 0.0

    def test_get_weather__should_return_min_temp_value(self, mock_city, mock_forecast):
        mock_forecast.return_value = self.FORECAST_RESPONSE
        mock_city.return_value = self.CITY_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.minTemp == self.DAY['temperature_2m_min'][0]

    def test_get_weather__should_return_default_min_temp_value(self, mock_city, mock_forecast):
        self.FORECAST_RESPONSE = {'daily': {}, 'current_weather': self.TEMP}
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.minTemp == 0.0

    def test_get_weather__should_return_max_temp_value(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.maxTemp == self.DAY['temperature_2m_max'][0]

    def test_get_weather__should_return_default_max_temp_value(self, mock_city, mock_forecast):
        self.FORECAST_RESPONSE = {'daily': {}, 'current_weather': self.TEMP}
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.maxTemp == 0.0

    def test_get_weather__should_return_weather_description(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.description == 'partly cloudy'

    def test_get_weather__should_return_default_weather_description(self, mock_city, mock_forecast):
        self.FORECAST_RESPONSE = {'daily': self.DAY, 'current_weather': {}}
        mock_city.return_value = self.CITY_RESPONSE
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.description == 'sunny'

    def test_get_weather__should_return_default_values_when_not_ok_status_returned(self, mock_city, mock_forecast):
        mock_city.return_value = {}
        mock_forecast.return_value = self.FORECAST_RESPONSE

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.temp == 0.0
        assert actual.minTemp == 0.0
        assert actual.maxTemp == 0.0
        assert actual.description == 'sunny'

    def test_get_weather__should_return_default_values_when_throws_connection_error(self, mock_city, mock_forecast):
        mock_city.side_effect = ConnectionError()

        actual = get_weather(self.CITY, self.UNIT)

        assert actual.temp == 0.0
        assert actual.minTemp == 0.0
        assert actual.maxTemp == 0.0
        assert actual.description == 'sunny'
        
    def test_get_weather__should_make_call_to_get_city_coords(self, mock_city, mock_forecast):
        get_weather(self.CITY, self.UNIT)
        mock_city.assert_called_with(self.CITY)

    def test_get_weather__should_call_forecast_using_coords_from_weather_call(self, mock_city, mock_forecast):
        mock_city.return_value = self.CITY_RESPONSE
        get_weather(self.CITY, self.UNIT)
        mock_forecast.assert_called_with(self.COORDS['latitude'], self.COORDS['longitude'], self.UNIT)
