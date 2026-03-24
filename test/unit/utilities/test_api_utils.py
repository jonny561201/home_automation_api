import json
from datetime import datetime

import pytest
from mock import patch, ANY
from requests import Response, ReadTimeout, ConnectTimeout
from werkzeug.exceptions import FailedDependency, BadRequest, Unauthorized

from svc.config.settings_state import Settings
from svc.utilities.api_utils import get_city_coordinates, create_light_group, set_light_groups, set_light_state, \
    get_light_groups, get_garage_door_status, toggle_garage_door_state, update_garage_door_state, \
    send_new_account_email, get_forecast_by_coords, exchange_auth0_code


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
        self.WEATHER_PARAMS = {'name': self.CITY, 'count': 1}
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
class TestGarageApiRequests:
    GARAGE_ID = 5
    BASE_URL = 'http://localhost:80'
    FAKE_BEARER = 'fakeBearerToken'
    STATE = {'isGarageOpen': False}
    STATUS = {'isGarageOpen': True, 'statusDuration': datetime.now().isoformat(), 'coordinates': {'latitude': 12.34, 'longitude': -56.78}}

    def test_get_garage_door_status__should_call_requests_with_url(self, mock_requests):
        response = Response()
        response.status_code = 200
        mock_requests.get.return_value = response
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

        expected_url = f'{self.BASE_URL}/garageDoor/{str(self.GARAGE_ID)}/status'
        mock_requests.get.assert_called_with(expected_url, headers=ANY, timeout=5)

    def test_get_garage_door_status__should_call_requests_with_headers(self, mock_requests):
        response = Response()
        response.status_code = 200
        mock_requests.get.return_value = response
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        expected_headers = {'Authorization': 'Bearer ' + self.FAKE_BEARER}
        get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

        mock_requests.get.assert_called_with(ANY, headers=expected_headers, timeout=5)

    def test_get_garage_door_status__should_return_response(self, mock_requests):
        response = Response()
        response.status_code = 200
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        mock_requests.get.return_value = response
        actual = get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

        assert actual.to_dict() == self.STATUS

    def test_get_garage_door_status__should_raise_failed_dependency_when_request_raises_connection_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectionError()
        with pytest.raises(FailedDependency):
            get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

    def test_get_garage_door_status__should_raise_failed_dependency_when_request_raises_connection_timeout_error(self, mock_requests):
        mock_requests.get.side_effect = ConnectTimeout()
        with pytest.raises(FailedDependency):
            get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

    def test_get_garage_door_status__should_raise_bad_request_when_failure_status_code(self, mock_requests):
        response = Response()
        response.status_code = 400
        mock_requests.get.return_value = response
        with pytest.raises(BadRequest) as e:
            get_garage_door_status(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)
        assert e.value.description == 'Garage node returned a failure'

    def test_toggle_garage_door_state__should_call_requests_with_url(self, mock_requests):
        response = Response()
        response.status_code = 200
        mock_requests.get.return_value = response
        toggle_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

        expected_url = f'{self.BASE_URL}/garageDoor/{str(self.GARAGE_ID)}/toggle'
        mock_requests.get.assert_called_with(expected_url, headers=ANY, timeout=5)

    def test_toggle_garage_door_state__should_call_requests_with_with_headers(self, mock_requests):
        response = Response()
        response.status_code = 200
        mock_requests.get.return_value = response
        header = {'Authorization': 'Bearer ' + self.FAKE_BEARER}
        toggle_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)

        mock_requests.get.assert_called_with(ANY, headers=header, timeout=5)

    def test_toggle_garage_door_state__should_raise_bad_request_when_status_code_failure(self, mock_request):
        response = Response()
        response.status_code = 400
        mock_request.get.return_value = response
        with pytest.raises(BadRequest) as e:
            toggle_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)
        assert e.value.description == 'Garage node returned a failure'

    def test_toggle_garage_door_state__should_raise_bad_request_when_request_raises_connection_error(self, mock_request):
        mock_request.get.side_effect = ConnectionError()
        with pytest.raises(BadRequest) as e:
            toggle_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)
        assert e.value.description == 'Garage node returned a failure'

    def test_toggle_garage_door_state__should_raise_bad_request_when_request_raises_connection_timeout_error(self, mock_request):
        mock_request.get.side_effect = ConnectTimeout()
        with pytest.raises(BadRequest) as e:
            toggle_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID)
        assert e.value.description == 'Garage node returned a failure'

    def test_update_garage_door_state__should_call_requests_with_url(self, mock_requests):
        request = {}
        response = Response()
        response.status_code = 200
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        mock_requests.post.return_value = response
        update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)

        expected_url = f'{self.BASE_URL}/garageDoor/{str(self.GARAGE_ID)}/state'
        mock_requests.post.assert_called_with(expected_url, headers=ANY, data=ANY, timeout=5)

    def test_update_garage_door_state__should_call_requests_with_headers(self, mock_requests):
        header = {'Authorization': 'Bearer ' + self.FAKE_BEARER}
        request = {}
        response = Response()
        response.status_code = 200
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        mock_requests.post.return_value = response
        update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)

        mock_requests.post.assert_called_with(ANY, headers=header, data=ANY, timeout=5)

    def test_update_garage_door_state__should_call_requests_with_request(self, mock_requests):
        request = '{"testData": "NotReal"}'.encode()
        response = Response()
        response.status_code = 200
        response._content = json.dumps(self.STATUS).encode('UTF-8')
        mock_requests.post.return_value = response
        update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)

        mock_requests.post.assert_called_with(ANY, headers=ANY, data=request, timeout=5)

    def test_update_garage_door_state__should_raise_bad_request_when_response_is_failure_status(self, mock_requests):
        response = Response()
        response.status_code = 400
        mock_requests.post.return_value = response
        request = '{"testData": "NotReal"}'.encode()
        with pytest.raises(BadRequest) as e:
            update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)
        assert e.value.description == 'Garage node returned a failure'

    def test_update_garage_door_state__should_raise_bad_request_when_response_raises_connection_error(self, mock_requests):
        mock_requests.post.side_effect = ConnectionError()
        request = '{"testData": "NotReal"}'.encode()
        with pytest.raises(BadRequest) as e:
            update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)
        assert e.value.description == 'Garage node returned a failure'

    def test_update_garage_door_state__should_raise_bad_request_when_response_raises_connection_timeout_error(self, mock_requests):
        mock_requests.post.side_effect = ConnectTimeout()
        request = '{"testData": "NotReal"}'.encode()
        with pytest.raises(BadRequest) as e:
            update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)
        assert e.value.description == 'Garage node returned a failure'

    def test_update_garage_door_state__should_return_response(self, mock_requests):
        response = Response()
        request = {}
        response.status_code = 200
        response._content = json.dumps(self.STATE).encode('UTF-8')
        mock_requests.post.return_value = response
        actual = update_garage_door_state(self.FAKE_BEARER, self.BASE_URL, self.GARAGE_ID, request)

        assert actual.to_dict() == self.STATE


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

        mock_requests.post.assert_called_with(expected_url, data=ANY, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_off_set(self, mock_requests):
        brightness = 222
        mock_requests.post.return_value = self.__create_response()
        group_id = 2
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = json.dumps({'groupId': group_id, 'on': True, 'brightness': brightness})
        mock_requests.post.assert_called_with(ANY, data=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_to_false_when_brightness_zero(self, mock_requests):
        mock_requests.post.return_value = self.__create_response()
        group_id = 2
        set_light_groups(self.API_KEY, group_id, True, 0)

        expected_request = json.dumps({'groupId': group_id, 'on': False})
        mock_requests.post.assert_called_with(ANY, data=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_dimmer_value(self, mock_requests):
        brightness = 233
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = json.dumps({'groupId': group_id, 'on': True, 'brightness': brightness})
        mock_requests.post.assert_called_with(ANY, data=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_call_state_with_on_set_true_if_dimmer_value(self, mock_requests):
        brightness = 155
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, True, brightness)

        expected_request = json.dumps({'groupId': group_id, 'on': True, 'brightness': brightness})
        mock_requests.post.assert_called_with(ANY, data=expected_request, headers={'LightApiKey': self.API_KEY})

    def test_set_light_groups__should_raise_failed_dependency_when_returns_failure(self, mock_requests):
        brightness = 155
        mock_requests.post.return_value = self.__create_response(status=400)
        with pytest.raises(FailedDependency):
            set_light_groups(self.API_KEY, 1, True, brightness)

    def test_set_light_groups__should_call_api_with_no_brightness_when_not_supplied(self, mock_requests):
        mock_requests.post.return_value = self.__create_response()
        group_id = 1
        set_light_groups(self.API_KEY, group_id, False, None)
        expected = json.dumps({'groupId': group_id, 'on': False})

        mock_requests.post.assert_called_with(ANY, data=expected, headers={'LightApiKey': self.API_KEY})

    def test_create_light_group__should_make_api_call_to_url(self, mock_requests):
        expected_url = f'{self.BASE_URL}/group/create'
        create_light_group(self.API_KEY, None)

        mock_requests.post.assert_called_with(expected_url, data=ANY, headers={'LightApiKey': self.API_KEY})

    def test_create_light_group__should_make_api_with_group_name(self, mock_requests):
        group_name = 'Test Group'
        expected_data = json.dumps({'name': group_name})
        create_light_group(self.API_KEY, group_name)

        mock_requests.post.assert_called_with(ANY, data=expected_data, headers={'LightApiKey': self.API_KEY})

    # def test_get_all_lights__should_make_api_call_to_url(self, mock_requests):
    #     mock_requests.get.return_value = self.__create_response()
    #     expected_url = f'{self.BASE_URL}/{self.API_KEY}/lights'
    #     get_all_lights(self.API_KEY)
    #
    #     mock_requests.get.assert_called_with(expected_url)
    #
    # def test_get_all_lights__should_return_response_from_api(self, mock_requests):
    #     response_data = {'light_name': 'DoesntMatter'}
    #     mock_requests.get.return_value = self.__create_response(data=response_data)
    #     actual = get_all_lights(self.API_KEY)
    #
    #     assert actual == response_data
    #
    # def test_get_all_lights__should_raise_failed_dependency_when_node_returns_500(self, mock_requests):
    #     mock_requests.get.return_value = self.__create_response(status=500)
    #     with pytest.raises(FailedDependency):
    #         get_all_lights(self.API_KEY)
    #
    # def test_get_all_lights__should_raise_failed_dependency_when_node_returns_400(self, mock_requests):
    #     mock_requests.get.return_value = self.__create_response(status=400)
    #     with pytest.raises(FailedDependency):
    #         get_all_lights(self.API_KEY)
    #
    # def test_get_all_lights__should_raise_failed_dependency_when_request_raises_connection_error(self, mock_requests):
    #     mock_requests.get.side_effect = ConnectionError()
    #     with pytest.raises(FailedDependency):
    #         get_all_lights(self.API_KEY)
    #
    # def test_get_all_lights__should_raise_failed_dependency_when_request_raises_connection_timeout_error(self, mock_requests):
    #     mock_requests.get.side_effect = ConnectTimeout()
    #     with pytest.raises(FailedDependency):
    #         get_all_lights(self.API_KEY)
    #
    # def test_get_light_group_attributes__should_make_api_call_to_url(self, mock_requests):
    #     group_id = "4"
    #     mock_requests.get.return_value = self.__create_response()
    #     expected_url = f'{self.BASE_URL}/{self.API_KEY}/groups/{group_id}'
    #     get_light_group_attributes(self.API_KEY, group_id)
    #
    #     mock_requests.get.assert_called_with(expected_url)
    #
    # def test_get_light_group_attributes__should_return_response_from_api(self, mock_requests):
    #     group_id = "12"
    #     response_data = {'lights': ['1', '2']}
    #     mock_requests.get.return_value = self.__create_response(data=response_data)
    #     actual = get_light_group_attributes(self.API_KEY, group_id)
    #
    #     assert actual == response_data
    #
    # def test_get_light_group_attributes__should_raise_failed_dependency_when_node_returns_500(self, mock_requests):
    #     group_id = '11'
    #     mock_requests.get.return_value = self.__create_response(status=500)
    #     with pytest.raises(FailedDependency):
    #         get_light_group_attributes(self.API_KEY, group_id)
    #
    # def test_get_light_group_attributes__should_raise_failed_dependency_when_node_returns_400(self, mock_requests):
    #     group_id = '3'
    #     mock_requests.get.return_value = self.__create_response(status=400)
    #     with pytest.raises(FailedDependency):
    #         get_light_group_attributes(self.API_KEY, group_id)
    #
    # def test_get_light_group_attributes__should_raise_failed_dependency_when_request_raises_connection_error(self, mock_requests):
    #     group_id = '3'
    #     mock_requests.get.side_effect = ConnectionError()
    #     with pytest.raises(FailedDependency):
    #         get_light_group_attributes(self.API_KEY, group_id)
    #
    # def test_get_light_group_attributes__should_raise_failed_dependency_when_request_raises_connection_timeout_error(self, mock_requests):
    #     group_id = '3'
    #     mock_requests.get.side_effect = ConnectTimeout()
    #     with pytest.raises(FailedDependency):
    #         get_light_group_attributes(self.API_KEY, group_id)
    #
    # def test_get_light_state__should_make_api_call_to_url(self, mock_requests):
    #     light_id = "4"
    #     expected_url = f'{self.BASE_URL}/{self.API_KEY}/lights/{light_id}'
    #     mock_requests.get.return_value = self.__create_response()
    #     get_light_state(self.API_KEY, light_id)
    #
    #     mock_requests.get.assert_called_with(expected_url)
    #
    # def test_get_light_state__should_return_response_from_api(self, mock_requests):
    #     light_id = '5'
    #     response_data = {'name': 'livingRoomLamp', 'state': {'on': True}}
    #     mock_requests.get.return_value = self.__create_response(data=response_data)
    #
    #     actual = get_light_state(self.API_KEY, light_id)
    #
    #     assert actual == response_data
    #
    # def test_get_light_state__should_raise_failed_dependency_when_node_returns_500(self, mock_requests):
    #     light_id = '12'
    #     mock_requests.get.return_value = self.__create_response(status=500)
    #     with pytest.raises(FailedDependency):
    #         get_light_state(self.API_KEY, light_id)
    #
    # def test_get_light_state__should_raise_failed_dependency_when_node_returns_400(self, mock_requests):
    #     light_id = '12'
    #     mock_requests.get.return_value = self.__create_response(status=400)
    #     with pytest.raises(FailedDependency):
    #         get_light_state(self.API_KEY, light_id)
    #
    # def test_get_light_state__should_raise_failed_dependency_when_request_raises_connection_error(self, mock_requests):
    #     light_id = '12'
    #     mock_requests.get.side_effect = ConnectionError()
    #     with pytest.raises(FailedDependency):
    #         get_light_state(self.API_KEY, light_id)
    #
    # def test_get_light_state__should_raise_failed_dependency_when_request_raises_connection_timeout_error(self, mock_requests):
    #     light_id = '12'
    #     mock_requests.get.side_effect = ConnectTimeout()
    #     with pytest.raises(FailedDependency):
    #         get_light_state(self.API_KEY, light_id)

    # TODO: test assign light group

    def test_set_light_state__should_make_call_to_api(self, mock_requests):
        light_id = '7'
        expected_url = f'{self.BASE_URL}/light/state'
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, None)

        mock_requests.post.assert_called_with(expected_url, data=ANY, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_submit_data_to_requested_url(self, mock_requests):
        light_id = '9'
        brightness = 188
        expected_data = json.dumps({'lightId': light_id, 'on': True, 'brightness': brightness})
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, brightness)

        mock_requests.post.assert_called_with(ANY, data=expected_data, headers={'LightApiKey': self.API_KEY})

    def test_set_light_state__should_set_light_on_state_to_false_when_brightness_zero(self, mock_requests):
        light_id = '9'
        brightness = 0
        expected_data = json.dumps({'lightId': light_id, 'on': False, 'brightness': brightness})
        mock_requests.post.return_value = self.__create_response()
        set_light_state(self.API_KEY, light_id, brightness)

        mock_requests.post.assert_called_with(ANY, data=expected_data, headers={'LightApiKey': self.API_KEY})

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
class TestEmailApiRequests:
    EMAIL = 'test@test.com'
    PASSWORD = 'fakePassword'
    API_KEY = 'asdjfhv323240'
    URL = 'https://test.email.api'

    def setup_method(self):
        Settings.get_instance()._settings = {'EmailAppId': self.API_KEY}
        Settings.get_instance().BaseUrls._settings = {'Email': self.URL}

    def test_send_new_account_email__should_pass_api_key_to_header_in_requests(self, mock_request):
        expected_header = {'api-key': self.API_KEY, 'content-type': 'application/json', 'accept': 'application/json'}
        send_new_account_email(self.EMAIL, self.PASSWORD)

        mock_request.post.assert_called_with(ANY, data=ANY, headers=expected_header)

    def test_send_new_account_email__should_call_url_in_post_method(self, mock_request):
        send_new_account_email(self.EMAIL, self.PASSWORD)

        mock_request.post.assert_called_with(self.URL, data=ANY, headers=ANY)

    def test_send_new_account_email__should_make_call_to_post_request_with_correct_body(self, mock_request):
        expected_data = {
            "sender": {"name": "Home Automation", "email": 'senderalex@example.com'},
            "to": [{"email": self.EMAIL, "name": "Your Name"}],
            "subject": "Home Automation: New Account Registration",
            "htmlContent": f"<html><head></head><body><p>Hello,</p><p>A new Home Automation account has been setup for you.</p><p>Password: {self.PASSWORD}</p></body></html>"
        }
        send_new_account_email(self.EMAIL, self.PASSWORD)

        mock_request.post.assert_called_with(ANY, data=json.dumps(expected_data), headers=ANY)


@patch('svc.utilities.api_utils.requests')
class TestExchangeAuth0Code:
    FAKE_CODE = 'fake_auth_code'
    FAKE_VERIFIER = 'fake_verifier'
    FAKE_REDIRECT = 'http://localhost:3000/callback'
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

