import jwt
import pytest
from mock import patch
from werkzeug.exceptions import BadRequest

from svc.controllers.geocode_controller import reverse_geocode


@patch('svc.controllers.geocode_controller.get_census_reverse_geocode')
@patch('svc.controllers.geocode_controller.AuthClient')
class TestReverseGeocode:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    LATITUDE = 41.5868
    LONGITUDE = -93.625

    def setup_method(self):
        self.census_response = {
            'result': {
                'geographies': {
                    'States': [{'STUSAB': 'IA', 'BASENAME': 'Iowa'}],
                    'Incorporated Places': [{'BASENAME': 'Des Moines'}],
                    'Census Designated Places': [{'BASENAME': 'Some CDP'}],
                    'Counties': [{'BASENAME': 'Polk'}],
                }
            }
        }

    def test_reverse_geocode__should_validate_bearer_token(self, mock_jwt, mock_census):
        mock_census.return_value = self.census_response
        reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_reverse_geocode__should_call_census_with_lat_and_lon(self, mock_jwt, mock_census):
        mock_census.return_value = self.census_response
        reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        mock_census.assert_called_with(self.LATITUDE, self.LONGITUDE)

    def test_reverse_geocode__should_raise_bad_request_when_latitude_missing(self, mock_jwt, mock_census):
        with pytest.raises(BadRequest):
            reverse_geocode(self.BEARER_TOKEN, None, self.LONGITUDE)

    def test_reverse_geocode__should_raise_bad_request_when_longitude_missing(self, mock_jwt, mock_census):
        with pytest.raises(BadRequest):
            reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, None)

    def test_reverse_geocode__should_return_state_code_from_census(self, mock_jwt, mock_census):
        mock_census.return_value = self.census_response
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual['state'] == 'IA'

    def test_reverse_geocode__should_prefer_incorporated_place_for_city(self, mock_jwt, mock_census):
        mock_census.return_value = self.census_response
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual['city'] == 'Des Moines'

    def test_reverse_geocode__should_fallback_to_census_designated_place(self, mock_jwt, mock_census):
        self.census_response['result']['geographies']['Incorporated Places'] = []
        mock_census.return_value = self.census_response
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual['city'] == 'Some CDP'

    def test_reverse_geocode__should_fallback_to_county(self, mock_jwt, mock_census):
        self.census_response['result']['geographies']['Incorporated Places'] = []
        self.census_response['result']['geographies']['Census Designated Places'] = []
        mock_census.return_value = self.census_response
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual['city'] == 'Polk'

    def test_reverse_geocode__should_return_empty_when_no_states(self, mock_jwt, mock_census):
        mock_census.return_value = {'result': {'geographies': {}}}
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual == {}

    def test_reverse_geocode__should_return_empty_when_no_city_match(self, mock_jwt, mock_census):
        mock_census.return_value = {
            'result': {
                'geographies': {
                    'States': [{'STUSAB': 'IA'}],
                    'Incorporated Places': [],
                    'Census Designated Places': [],
                    'Counties': [],
                }
            }
        }
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual == {}

    def test_reverse_geocode__should_return_empty_when_state_code_missing(self, mock_jwt, mock_census):
        mock_census.return_value = {
            'result': {
                'geographies': {
                    'States': [{}],
                    'Incorporated Places': [{'BASENAME': 'Des Moines'}],
                }
            }
        }
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual == {}

    def test_reverse_geocode__should_return_empty_when_response_missing_result(self, mock_jwt, mock_census):
        mock_census.return_value = {}
        actual = reverse_geocode(self.BEARER_TOKEN, self.LATITUDE, self.LONGITUDE)
        assert actual == {}
