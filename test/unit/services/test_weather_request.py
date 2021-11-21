import json

import pytest
from mock import patch
from requests.exceptions import ConnectionError
from werkzeug.exceptions import Unauthorized

from svc.services.weather_request import get_weather


@patch('svc.services.weather_request.get_weather_by_city')
class TestWeatherRequest:
    CITY = 'Prague'
    UNIT = 'metric'
    APP_ID = 'abc123'
    MOCK_RESPONSE = None
    STATUS_OK = 200
    STATUS_BAD = 400
    STATUS_UNAUTHORIZED = 401

    def setup_method(self):
        self.MOCK_RESPONSE = {'main': {}, 'weather': [{}]}

    def test_get_weather__should_return_temp_data(self, mock_request):
        expected_temp = 64.8
        self.MOCK_RESPONSE['main']['temp'] = expected_temp
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == expected_temp

    def test_get_weather__should_return_default_temp_value_of_zero(self, mock_request):
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0

    def test_get_weather__should_return_min_temp_value(self, mock_request):
        min_temp = 12.34
        self.MOCK_RESPONSE['main']['temp_min'] = min_temp
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['minTemp'] == min_temp

    def test_get_weather__should_return_default_min_temp_value(self, mock_request):
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['minTemp'] == 0.0

    def test_get_weather__should_return_max_temp_value(self, mock_request):
        max_temp = 12.87
        self.MOCK_RESPONSE['main']['temp_max'] = max_temp
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['maxTemp'] == max_temp

    def test_get_weather__should_return_default_max_temp_value(self, mock_request):
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['maxTemp'] == 0.0

    def test_get_weather__should_return_weather_description(self, mock_request):
        forecast_description = 'fake forecast'
        self.MOCK_RESPONSE['weather'][0]['description'] = forecast_description
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['description'] == forecast_description

    def test_get_weather__should_return_default_weather_description(self, mock_request):
        mock_request.return_value = self.MOCK_RESPONSE

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['description'] == ""

    def test_get_weather__should_return_default_values_when_not_ok_status_returned(self, mock_request):
        mock_request.return_value = {}

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0
        assert actual['minTemp'] == 0.0
        assert actual['maxTemp'] == 0.0
        assert actual['description'] == ""

    def test_get_weather__should_return_default_values_when_throws_connection_error(self, mock_request):
        mock_request.side_effect = ConnectionError()

        actual = get_weather(self.CITY, self.UNIT, self.APP_ID)

        assert actual['temp'] == 0.0
        assert actual['minTemp'] == 0.0
        assert actual['maxTemp'] == 0.0
        assert actual['description'] == ""
