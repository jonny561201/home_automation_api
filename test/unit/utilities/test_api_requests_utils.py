import json

from mock import patch, ANY
from requests import Response

from svc.constants.home_automation import Automation
from svc.utilities.api_requests_utils import get_weather_by_city, get_light_api_key


@patch('svc.utilities.api_requests_utils.requests')
class TestWeatherApiRequests:
    CITY = 'Des Moines'
    UNIT_PREFERENCE = 'imperial'
    URL = 'https://api.openweathermap.org/data/2.5/weather'
    APP_ID = 'ab30xkd0'
    PARAMS = None
    RESPONSE = None
    RESPONSE_CONTENT = None

    def setup_method(self):
        self.RESPONSE = Response()
        self.RESPONSE.status_code = 200
        self.RESPONSE_CONTENT = {'main': {}, 'weather': [{}]}
        self.PARAMS = {'q': self.CITY, 'units': self.UNIT_PREFERENCE, 'APPID': self.APP_ID}

    def test_get_weather_by_city__should_call_requests_get(self, mock_requests):
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT)
        mock_requests.get.return_value = self.RESPONSE

        get_weather_by_city(self.CITY, self.UNIT_PREFERENCE, self.APP_ID)

        mock_requests.get.assert_called_with(self.URL, params=self.PARAMS)

    def test_get_weather_by_city__should_use_provided_city_location_in_url(self, mock_requests):
        city = 'London'
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT)
        mock_requests.get.return_value = self.RESPONSE

        get_weather_by_city(city, self.UNIT_PREFERENCE, self.APP_ID)

        self.PARAMS['q'] = city
        mock_requests.get.assert_called_with(self.URL, params=self.PARAMS)

    def test_get_weather_by_city__should_use_provided_app_id_in_url(self, mock_requests):
        app_id = 'fake app id'
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT)
        mock_requests.get.return_value = self.RESPONSE

        get_weather_by_city(self.CITY, self.UNIT_PREFERENCE, app_id)

        self.PARAMS['APPID'] = app_id
        mock_requests.get.assert_called_with(self.URL, params=self.PARAMS)

    def test_get_weather_by_city__should_call_api_using_unit_preference_in_params(self, mock_requests):
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT)
        mock_requests.get.return_value = self.RESPONSE
        unit = 'metric'
        self.PARAMS['units'] = unit

        get_weather_by_city(self.CITY, unit, self.APP_ID)

        mock_requests.get.assert_called_with(self.URL, params=self.PARAMS)

    def test_get_weather_by_city__should_return_status_code_and_content(self, mock_requests):
        expected_content = json.dumps(self.RESPONSE_CONTENT)
        self.RESPONSE._content = expected_content
        mock_requests.get.return_value = self.RESPONSE

        status, content = get_weather_by_city(self.CITY, 'metric', self.APP_ID)

        assert status == 200
        assert content == expected_content


@patch('svc.utilities.api_requests_utils.requests')
class TestLightApiRequests:

    USERNAME = 'fake username'
    PASSWORD = 'fake password'
    URL = 'http://192.168.1.139:8080/api'

    def test_get_light_api_key__should_call_requests_with_url(self, mock_requests):
        get_light_api_key(self.USERNAME, self.PASSWORD)

        mock_requests.post.assert_called_with(self.URL, data=ANY, headers=ANY)

    def test_get_light_api_key__should_call_requests_with_device_type(self, mock_requests):
        get_light_api_key(self.USERNAME, self.PASSWORD)

        body = json.dumps({'devicetype': Automation().APP_NAME})
        mock_requests.post.assert_called_with(ANY, data=body, headers=ANY)

    def test_get_light_api_key__should_provide_username_and_pass_as_auth_header(self, mock_requests):
        get_light_api_key(self.USERNAME, self.PASSWORD)

        headers = {'Authorization': 'Basic ' + 'ZmFrZSB1c2VybmFtZTpmYWtlIHBhc3N3b3Jk'}
        mock_requests.post.assert_called_with(ANY, data=ANY, headers=headers)
