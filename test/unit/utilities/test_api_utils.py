import json

import pytest
from mock import patch, ANY
from requests import Response, ReadTimeout, ConnectTimeout
from werkzeug.exceptions import FailedDependency, Unauthorized

from svc.config.settings_state import Settings
from svc.utilities.api_utils import (get_city_coordinates, set_light_groups, set_light_state, get_light_groups,
                                     get_forecast_by_coords, exchange_auth0_code, create_auth0_user, assign_auth0_roles,
                                     send_auth0_password_reset, register_home_automation_device,
                                     get_census_reverse_geocode)


@patch('svc.utilities.api_utils.requests')
class TestWeatherApiRequests:
    CITY = 'Des Moines'
    COORDS = {'lat': 23.123, 'lon': -92.28876}
    UNIT_PREFERENCE = 'fahrenheit'
    URL = 'test.weather.api'

    def setup_method(self):
        Settings.get_instance().BaseUrls._settings = {'Weather': self.URL}
        self.RESPONSE = Response()
        self.RESPONSE.status_code = 200
        self.RESPONSE_CONTENT = {'weather': [{}]}
        self.WEATHER_PARAMS = {'name': self.CITY, 'count': 1, 'country': 'US', 'admin1': None}
        self.FORECAST_PARAMS = {'latitude': self.COORDS['lat'], 'longitude': self.COORDS['lon'], 'current_weather': True, 'temperature_unit': self.UNIT_PREFERENCE, 'daily': 'temperature_2m_max,temperature_2m_min,weathercode', 'forecast_days': 1, 'timezone': 'auto'}

    def test_get_city_coordinates__should_call_requests_get(self, mock_requests):
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT).encode('UTF-8')
        mock_requests.get.return_value = self.RESPONSE

        get_city_coordinates(self.CITY)

        mock_requests.get.assert_called_with(f'https://geocoding-{self.URL}/search', params=self.WEATHER_PARAMS)

    def test_get_city_coordinates__should_use_provided_city_location_in_url(self, mock_requests):
        self.RESPONSE._content = json.dumps(self.RESPONSE_CONTENT).encode('UTF-8')
        mock_requests.get.return_value = self.RESPONSE

        get_city_coordinates(self.WEATHER_PARAMS['name'])

        mock_requests.get.assert_called_with(f'https://geocoding-{self.URL}/search', params=self.WEATHER_PARAMS)

    def test_get_city_coordinates__should_return_status_code_and_content(self, mock_requests):
        expected_content = json.dumps(self.RESPONSE_CONTENT).encode('UTF-8')
        self.RESPONSE._content = expected_content
        mock_requests.get.return_value = self.RESPONSE

        content = get_city_coordinates(self.CITY)

        assert content == self.RESPONSE_CONTENT

    def test_get_city_coordinates__should_raise_unauthorized(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.get.return_value = self.RESPONSE
        with pytest.raises(Unauthorized):
            get_city_coordinates(self.CITY)

    def test_get_forecast_by_coords__should_make_get_request(self, mock_requests):
        self.RESPONSE._content = json.dumps({}).encode('UTF-8')
        mock_requests.get.return_value = self.RESPONSE
        get_forecast_by_coords(self.COORDS['lat'], self.COORDS['lon'], self.UNIT_PREFERENCE)

        mock_requests.get.assert_called_with(f'https://{self.URL}/forecast', params=self.FORECAST_PARAMS)

    def test_get_forecast_by_coords__should_return_the_response_content(self, mock_requests):
        content = {'doesntMatter': 'dumb'}
        self.RESPONSE._content = json.dumps(content).encode('UTF-8')
        mock_requests.get.return_value = self.RESPONSE

        actual = get_forecast_by_coords(self.COORDS['lat'], self.COORDS['lon'], self.UNIT_PREFERENCE)

        assert actual == content

    def test_get_forecast_by_coords__should_raise_failed_dependency_when_bad_response(self, mock_requests):
        self.RESPONSE.status_code = 400
        mock_requests.get.return_value = self.RESPONSE
        with pytest.raises(FailedDependency):
            get_forecast_by_coords(self.COORDS['lat'], self.COORDS['lon'], self.UNIT_PREFERENCE)

    def test_get_forecast_by_coords__should_raise_unauthorized(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.get.return_value = self.RESPONSE
        with pytest.raises(Unauthorized):
            get_forecast_by_coords(self.COORDS['lat'], self.COORDS['lon'], self.UNIT_PREFERENCE)


@patch('svc.utilities.api_utils.requests')
class TestCensusReverseGeocode:
    LATITUDE = 41.5868
    LONGITUDE = -93.625
    URL = 'https://geocoding.geo.census.gov/geocoder/geographies/coordinates'

    def setup_method(self):
        self.RESPONSE = Response()
        self.RESPONSE.status_code = 200
        self.CONTENT = {'result': {'geographies': {'States': [{'STUSAB': 'IA'}]}}}
        self.RESPONSE._content = json.dumps(self.CONTENT).encode('UTF-8')
        self.PARAMS = {
            'x': self.LONGITUDE,
            'y': self.LATITUDE,
            'benchmark': 'Public_AR_Current',
            'vintage': 'Current_Current',
            'format': 'json',
        }

    def test_get_census_reverse_geocode__should_call_requests_get_with_url_and_params(self, mock_requests):
        mock_requests.get.return_value = self.RESPONSE
        get_census_reverse_geocode(self.LATITUDE, self.LONGITUDE)
        mock_requests.get.assert_called_with(self.URL, params=self.PARAMS, timeout=10)

    def test_get_census_reverse_geocode__should_return_response_json(self, mock_requests):
        mock_requests.get.return_value = self.RESPONSE
        actual = get_census_reverse_geocode(self.LATITUDE, self.LONGITUDE)
        assert actual == self.CONTENT

    def test_get_census_reverse_geocode__should_raise_failed_dependency_on_bad_response(self, mock_requests):
        self.RESPONSE.status_code = 500
        mock_requests.get.return_value = self.RESPONSE
        with pytest.raises(FailedDependency):
            get_census_reverse_geocode(self.LATITUDE, self.LONGITUDE)

    def test_get_census_reverse_geocode__should_raise_unauthorized_on_401(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.get.return_value = self.RESPONSE
        with pytest.raises(Unauthorized):
            get_census_reverse_geocode(self.LATITUDE, self.LONGITUDE)


@patch('svc.utilities.api_utils.requests')
class TestRegisterGarageDevice:
    IP_ADDRESS = '192.168.0.100'
    IP_PORT = 5000

    def setup_method(self):
        self.RESPONSE = Response()
        self.RESPONSE._content = json.dumps({}).encode()
        self.RESPONSE.status_code = 200

    def test_register_garage_device__should_call_post_with_url(self, mock_requests):
        mock_requests.post.return_value = self.RESPONSE
        register_home_automation_device(self.IP_ADDRESS, self.IP_PORT)

        mock_requests.post.assert_called_with(f'http://{self.IP_ADDRESS}:{self.IP_PORT}/register', timeout=5, json=None)

    def test_register_garage_device__should_raise_failed_dependency_when_connection_error(self, mock_requests):
        mock_requests.post.side_effect = ConnectionError()
        with pytest.raises(FailedDependency):
            register_home_automation_device(self.IP_ADDRESS, self.IP_PORT)

    def test_register_garage_device__should_raise_failed_dependency_when_timeout(self, mock_requests):
        mock_requests.post.side_effect = ConnectTimeout()
        with pytest.raises(FailedDependency):
            register_home_automation_device(self.IP_ADDRESS, self.IP_PORT)

    def test_register_garage_device__should_raise_failed_dependency_when_bad_response(self, mock_requests):
        self.RESPONSE.status_code = 500
        mock_requests.post.return_value = self.RESPONSE
        with pytest.raises(FailedDependency):
            register_home_automation_device(self.IP_ADDRESS, self.IP_PORT)

    def test_register_garage_device__should_raise_unauthorized_when_401_response(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.post.return_value = self.RESPONSE
        with pytest.raises(Unauthorized):
            register_home_automation_device(self.IP_ADDRESS, self.IP_PORT)


@patch('svc.utilities.api_utils.requests')
class TestLightApiRequests:
    USERNAME = 'fake username'
    PASSWORD = 'fake password'
    BASE_URL = 'http://lights.test.api'
    API_KEY = 'fake api key'

    def test_get_light_groups__should_call_groups_url(self, mock_requests):
        Settings.get_instance().BaseUrls._settings = {'Lights': self.BASE_URL}
        expected_url = f'{self.BASE_URL}/groups'
        mock_requests.get.return_value = self.__create_response()
        get_light_groups(self.API_KEY)

        mock_requests.get.assert_called_with(expected_url, headers={'LightApiKey': self.API_KEY}, timeout=10)

    def test_get_light_groups__should_raise_failed_dependency_when_response_500(self, mock_requests):
        mock_requests.get.return_value = self.__create_response(status=500)
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY)

    def test_get_light_groups__should_raise_failed_dependency_when_response_400(self, mock_requests):
        mock_requests.get.return_value = self.__create_response(status=400)
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY)

    def test_get_light_groups__should_raise_failed_dependency_when_request_raises_connection_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError()
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY)

    def test_get_light_groups__should_raise_failed_dependency_when_request_raises_connection_timeout_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectTimeout()
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY)

    def test_get_light_groups__should_return_a_list_of_light_groups(self, mock_requests):
        response_data = {
            "1": {
                "devicemembership": [],
                "etag": "ab5272cfe11339202929259af22252ae",
                "hidden": False,
                "name": "Living Room"
            }
        }
        mock_requests.get.return_value = self.__create_response(data=response_data)
        actual = get_light_groups(self.API_KEY)

        assert actual['1']['etag'] == 'ab5272cfe11339202929259af22252ae'

    def test_set_light_groups__should_call_state_url(self, mock_requests):
        group_id = 1
        mock_requests.post.return_value = self.__create_response()
        expected_url = f'{self.BASE_URL}/group/state'
        set_light_groups(self.API_KEY, group_id, True, 132)

        mock_requests.post.assert_called_with(expected_url, json=ANY, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_off_set(self, mock_requests):
        brightness = 222
        mock_requests.post.return_value = self.__create_response()
        group_id = 2
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = {'groupId': group_id, 'on': True, 'brightness': brightness}
        mock_requests.post.assert_called_with(ANY, json=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_to_false_when_brightness_zero(self, mock_requests):
        mock_requests.post.return_value = self.__create_response()
        group_id = 2
        set_light_groups(self.API_KEY, group_id, True, 0)

        expected_request = {'groupId': group_id, 'on': False}
        mock_requests.post.assert_called_with(ANY, json=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_dimmer_value(self, mock_requests):
        brightness = 233
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = {'groupId': group_id, 'on': True, 'brightness': brightness}
        mock_requests.post.assert_called_with(ANY, json=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_set_true_if_dimmer_value(self, mock_requests):
        brightness = 155
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = {'groupId': group_id, 'on': True, 'brightness': brightness}
        mock_requests.post.assert_called_with(ANY, json=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_raise_failed_dependency_when_returns_failure(self, mock_requests):
        brightness = 155
        mock_requests.post.return_value = self.__create_response(status=400)
        with pytest.raises(FailedDependency):
            set_light_groups(self.API_KEY, 1, True, brightness)

    def test_set_light_groups__should_call_api_with_no_brightness_when_not_supplied(self, mock_requests):
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, False, None)
        expected = {'groupId': group_id, 'on': False}

        mock_requests.post.assert_called_with(ANY, json=expected, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_make_call_to_api(self, mock_requests):
        light_id = '7'
        expected_url = f'{self.BASE_URL}/light/state'
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, None)

        mock_requests.post.assert_called_with(expected_url, json=ANY, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_submit_data_to_requested_url(self, mock_requests):
        light_id = '9'
        brightness = 188
        expected_data = {'lightId': light_id, 'on': True, 'brightness': brightness}
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, brightness)

        mock_requests.post.assert_called_with(ANY, json=expected_data, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_set_light_on_state_to_false_when_brightness_zero(self, mock_requests):
        light_id = '9'
        brightness = 0
        expected_data = {'lightId': light_id, 'on': False, 'brightness': brightness}
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, brightness)

        mock_requests.post.assert_called_with(ANY, json=expected_data, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_raise_failed_dependency_when_exception(self, mock_requests):
        mock_requests.post.return_value = self.__create_response(400)
        with pytest.raises(FailedDependency):
            set_light_state(self.API_KEY, '4', 255)

    def test_get_full_state__should_make_call_to_api(self, mock_requests):
        mock_requests.get.return_value = self.__create_response()
        expected_url = f'{self.BASE_URL}/groups'
        get_light_groups(self.API_KEY)

        mock_requests.get.assert_called_with(expected_url, timeout=10, headers={'LightApiKey': self.API_KEY})

    def test_get_full_state__should_return_response_from_api(self, mock_requests):
        response_data = {'fakeResult': 'response'}
        mock_requests.get.return_value = self.__create_response(data=response_data)
        actual = get_light_groups(self.API_KEY, )

        assert actual == response_data

    def test_get_full_state__should_return_failed_dependency_when_light_node_returns_500(self, mock_requests):
        mock_requests.get.return_value = self.__create_response(status=500)
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY, )

    def test_get_full_state__should_return_failed_dependency_when_light_node_returns_400(self, mock_requests):
        mock_requests.get.return_value = self.__create_response(status=400)
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY, )

    def test_get_full_stat__should_not_fail_when_get_request_throws_connection_exception(self, mock_requests):
        mock_requests.get.side_effect = ReadTimeout()
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY, )

    def test_get_full_stat__should_not_fail_when_get_request_throws_connection_timeout_exception(self, mock_requests):
        mock_requests.get.side_effect = ConnectTimeout()
        with pytest.raises(FailedDependency):
            get_light_groups(self.API_KEY, )

    @staticmethod
    def __create_response(status=200, data={}):
        response = Response()
        response.status_code = status
        response._content = json.dumps(data).encode('UTF-8')
        return response


@patch('svc.utilities.api_utils.requests')
class TestAuth0Requests:
    FAKE_CODE = 'fake_auth_code'
    FAKE_VERIFIER = 'fake_verifier'
    FAKE_REDIRECT = 'http://localhost:3000/callback'
    DOMAIN = 'dev-test.us.auth0.com'
    CLIENT_ID = 'fake_client_id'
    CLIENT_SECRET = 'fake_client_secret'
    AUTH0_ID = 'auth0|abc123'
    ROLE_IDS = ['role_1', 'role_2']
    MANAGEMENT_TOKEN = 'fake_management_token'

    def setup_method(self):
        Settings.get_instance().Authority._settings = {
            'Domain': self.DOMAIN,
            'ClientId': self.CLIENT_ID,
            'ClientSecret': self.CLIENT_SECRET
        }
        self.TOKEN_RESPONSE = Response()
        self.TOKEN_RESPONSE.status_code = 200
        self.TOKEN_RESPONSE._content = json.dumps({'access_token': self.MANAGEMENT_TOKEN}).encode()
        self.RESPONSE = Response()
        self.RESPONSE.status_code = 200
        self.RESPONSE._content = '{}'.encode('utf-8')
        self.ROLES_RESPONSE = Response()
        self.ROLES_RESPONSE.status_code = 200
        self.ROLES_RESPONSE._content = b'{}'

    def test_exchange_auth0_code__should_call_auth0_token_endpoint(self, mock_requests):
        mock_requests.post.return_value = self.RESPONSE
        exchange_auth0_code(self.FAKE_CODE, self.FAKE_VERIFIER, self.FAKE_REDIRECT)

        request = {
            'grant_type': 'authorization_code',
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'code': self.FAKE_CODE,
            'code_verifier': self.FAKE_VERIFIER,
            'redirect_uri': self.FAKE_REDIRECT,
        }
        mock_requests.post.assert_called_with(f'https://{self.DOMAIN}/oauth/token', json=request)

    def test_exchange_auth0_code__should_return_token_response(self, mock_requests):
        self.RESPONSE._content = json.dumps({'access_token': 'abc', 'refresh_token': 'xyz'}).encode()
        mock_requests.post.return_value = self.RESPONSE
        actual = exchange_auth0_code(self.FAKE_CODE, self.FAKE_VERIFIER, self.FAKE_REDIRECT)

        assert actual == {'access_token': 'abc', 'refresh_token': 'xyz'}

    def test_exchange_auth0_code__should_raise_unauthorized_on_401(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.post.return_value = self.RESPONSE
        with pytest.raises(Unauthorized):
            exchange_auth0_code(self.FAKE_CODE, self.FAKE_VERIFIER, self.FAKE_REDIRECT)

    def test_exchange_auth0_code__should_raise_failed_dependency_on_500(self, mock_requests):
        self.RESPONSE.status_code = 500
        mock_requests.post.return_value = self.RESPONSE
        with pytest.raises(FailedDependency):
            exchange_auth0_code(self.FAKE_CODE, self.FAKE_VERIFIER, self.FAKE_REDIRECT)

    def test_assign_auth0_roles__should_call_roles_endpoint(self, mock_requests):
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.ROLES_RESPONSE]

        assign_auth0_roles(self.AUTH0_ID, self.ROLE_IDS)

        expected_headers = {'Authorization': f'Bearer {self.MANAGEMENT_TOKEN}', 'Content-Type': 'application/json'}
        mock_requests.post.assert_called_with(f'https://{self.DOMAIN}/api/v2/users/{self.AUTH0_ID}/roles', json={'roles': self.ROLE_IDS}, headers=expected_headers)

    def test_assign_auth0_roles__should_raise_unauthorized_on_401(self, mock_requests):
        self.ROLES_RESPONSE.status_code = 401
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.ROLES_RESPONSE]

        with pytest.raises(Unauthorized):
            assign_auth0_roles(self.AUTH0_ID, self.ROLE_IDS)

    def test_assign_auth0_roles__should_raise_failed_dependency_on_500(self, mock_requests):
        self.ROLES_RESPONSE.status_code = 500
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.ROLES_RESPONSE]

        with pytest.raises(FailedDependency):
            assign_auth0_roles(self.AUTH0_ID, self.ROLE_IDS)


@patch('svc.utilities.api_utils.generate_password')
@patch('svc.utilities.api_utils.requests')
class TestCreateAuth0User:
    EMAIL = 'child@test.com'
    DOMAIN = 'dev-test.us.auth0.com'
    CLIENT_ID = 'fake_client_id'
    CLIENT_SECRET = 'fake_client_secret'
    MANAGEMENT_TOKEN = 'fake_management_token'

    def setup_method(self):
        Settings.get_instance().Authority._settings = {
            'Domain': self.DOMAIN,
            'ClientId': self.CLIENT_ID,
            'ClientSecret': self.CLIENT_SECRET
        }
        self.TOKEN_RESPONSE = Response()
        self.TOKEN_RESPONSE.status_code = 200
        self.TOKEN_RESPONSE._content = json.dumps({'access_token': self.MANAGEMENT_TOKEN}).encode()
        self.USER_RESPONSE = Response()
        self.USER_RESPONSE.status_code = 200

    def test_create_auth0_user__should_call_users_endpoint(self, mock_requests, mock_password):
        mock_password.return_value = 'generated_pass'
        self.USER_RESPONSE._content = json.dumps({'user_id': 'auth0|123'}).encode()
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.USER_RESPONSE]

        create_auth0_user(self.EMAIL)

        expected_request = {
            'email': self.EMAIL,
            'password': 'generated_pass',
            'email_verified': False,
            'connection': 'Username-Password-Authentication',
        }
        expected_headers = {'Authorization': f'Bearer {self.MANAGEMENT_TOKEN}', 'Content-Type': 'application/json'}
        mock_requests.post.assert_called_with(f'https://{self.DOMAIN}/api/v2/users', json=expected_request, headers=expected_headers)

    def test_create_auth0_user__should_return_user_id(self, mock_requests, mock_password):
        mock_password.return_value = 'generated_pass'
        self.USER_RESPONSE._content = json.dumps({'user_id': 'auth0|123'}).encode()
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.USER_RESPONSE]

        actual = create_auth0_user(self.EMAIL)

        assert actual == 'auth0|123'

    def test_create_auth0_user__should_raise_unauthorized_on_401(self, mock_requests, mock_password):
        mock_password.return_value = 'generated_pass'
        self.USER_RESPONSE.status_code = 401
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.USER_RESPONSE]

        with pytest.raises(Unauthorized):
            create_auth0_user(self.EMAIL)

    def test_create_auth0_user__should_raise_failed_dependency_on_500(self, mock_requests, mock_password):
        mock_password.return_value = 'generated_pass'
        self.USER_RESPONSE.status_code = 500
        mock_requests.post.side_effect = [self.TOKEN_RESPONSE, self.USER_RESPONSE]

        with pytest.raises(FailedDependency):
            create_auth0_user(self.EMAIL)


@patch('svc.utilities.api_utils.requests')
class TestSendAuth0PasswordReset:
    EMAIL = 'child@test.com'
    DOMAIN = 'dev-test.us.auth0.com'
    CLIENT_ID = 'fake_client_id'
    CLIENT_SECRET = 'fake_client_secret'

    def setup_method(self):
        Settings.get_instance().Authority._settings = {
            'Domain': self.DOMAIN,
            'ClientId': self.CLIENT_ID,
            'ClientSecret': self.CLIENT_SECRET
        }
        self.RESPONSE = Response()
        self.RESPONSE.status_code = 200
        self.RESPONSE._content = b'{}'

    def test_send_auth0_password_reset__should_call_change_password_endpoint(self, mock_requests):
        mock_requests.post.return_value = self.RESPONSE

        send_auth0_password_reset(self.EMAIL)

        expected_request = {
            'client_id': self.CLIENT_ID,
            'email': self.EMAIL,
            'connection': 'Username-Password-Authentication',
        }
        mock_requests.post.assert_called_with(f'https://{self.DOMAIN}/dbconnections/change_password', json=expected_request)

    def test_send_auth0_password_reset__should_raise_unauthorized_on_401(self, mock_requests):
        self.RESPONSE.status_code = 401
        mock_requests.post.return_value = self.RESPONSE

        with pytest.raises(Unauthorized):
            send_auth0_password_reset(self.EMAIL)

    def test_send_auth0_password_reset__should_raise_failed_dependency_on_500(self, mock_requests):
        self.RESPONSE.status_code = 500
        mock_requests.post.return_value = self.RESPONSE

        with pytest.raises(FailedDependency):
            send_auth0_password_reset(self.EMAIL)

