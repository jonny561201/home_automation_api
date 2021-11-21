from mock import patch, ANY
from requests.exceptions import ConnectionError

from svc.services.weather_request import get_weather


@patch('svc.services.weather_request.get_forecast_by_coords')
@patch('svc.services.weather_request.get_weather_by_city')
class TestWeatherRequest:
    CITY = 'Prague'
    UNIT = 'metric'
    APP_ID = 'abc123'
    STATUS_OK = 200
    STATUS_BAD = 400
    STATUS_UNAUTHORIZED = 401
    COORDS = {'lat': 92.00, 'lon': -93.85}

    def setup_method(self):
        self.MOCK_RESPONSE = {'coord': self.COORDS, 'main': {}, 'weather': [{}]}

    def test_get_weather__should_return_temp_data(self, mock_weather, mock_forecast):
        expected_temp = 64.8
        self.MOCK_RESPONSE['main']['temp'] = expected_temp
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == expected_temp

    def test_get_weather__should_return_default_temp_value_of_zero(self, mock_weather, mock_forecast):
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0

    def test_get_weather__should_return_min_temp_value(self, mock_weather, mock_forecast):
        min_temp = 12.34
        self.MOCK_RESPONSE['main']['temp_min'] = min_temp
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['minTemp'] == min_temp

    def test_get_weather__should_return_default_min_temp_value(self, mock_weather, mock_forecast):
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['minTemp'] == 0.0

    def test_get_weather__should_return_max_temp_value(self, mock_weather, mock_forecast):
        max_temp = 12.87
        self.MOCK_RESPONSE['main']['temp_max'] = max_temp
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['maxTemp'] == max_temp

    def test_get_weather__should_return_default_max_temp_value(self, mock_weather, mock_forecast):
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['maxTemp'] == 0.0

    def test_get_weather__should_return_weather_description(self, mock_weather, mock_forecast):
        forecast_description = 'fake forecast'
        self.MOCK_RESPONSE['weather'][0]['description'] = forecast_description
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['description'] == forecast_description

    def test_get_weather__should_return_default_weather_description(self, mock_weather, mock_forecast):
        mock_weather.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['description'] == ""

    def test_get_weather__should_return_default_values_when_not_ok_status_returned(self, mock_weather, mock_forecast):
        mock_weather.return_value = {}

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0
        assert actual['minTemp'] == 0.0
        assert actual['maxTemp'] == 0.0
        assert actual['description'] == ""

    def test_get_weather__should_return_default_values_when_throws_connection_error(self, mock_weather, mock_forecast):
        mock_weather.side_effect = ConnectionError()

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0
        assert actual['minTemp'] == 0.0
        assert actual['maxTemp'] == 0.0
        assert actual['description'] == ""
        
    def test_get_weather__should_make_call_to_get_forecast_data(self, mock_weather, mock_forecast):
        get_weather(self.CITY, self.UNIT, self.APP_ID)
        mock_forecast.assert_called_with(ANY, self.UNIT, self.APP_ID)

    def test_get_weather__should_call_forecast_using_coords_from_weather_call(self, mock_weather, mock_forecast):
        mock_weather.return_value = self.MOCK_RESPONSE
        get_weather(self.CITY, self.UNIT, self.APP_ID)
        mock_forecast.assert_called_with(self.COORDS, ANY, ANY)
