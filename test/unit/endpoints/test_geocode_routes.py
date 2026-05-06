import json

from flask import Flask
from mock import patch, ANY

from svc.endpoints.geocode_routes import reverse_geocode


@patch('svc.endpoints.geocode_routes.geocode_controller')
class TestGeocodeRoutes:
    BEARER_TOKEN = 'fakeJwtToken'
    HEADERS = {'Authorization': BEARER_TOKEN}
    LATITUDE = 41.5868
    LONGITUDE = -93.625

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context(
            path=f'/geocode/reverse?latitude={self.LATITUDE}&longitude={self.LONGITUDE}',
            headers=self.HEADERS,
        )
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_reverse_geocode__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {}
        reverse_geocode()
        mock_controller.reverse_geocode.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_reverse_geocode__should_call_controller_with_latitude(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {}
        reverse_geocode()
        mock_controller.reverse_geocode.assert_called_with(ANY, self.LATITUDE, ANY)

    def test_reverse_geocode__should_call_controller_with_longitude(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {}
        reverse_geocode()
        mock_controller.reverse_geocode.assert_called_with(ANY, ANY, self.LONGITUDE)

    def test_reverse_geocode__should_call_controller_with_none_when_missing_args(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(path='/geocode/reverse', headers=self.HEADERS)
        self.ctx.push()
        mock_controller.reverse_geocode.return_value = {}
        reverse_geocode()
        mock_controller.reverse_geocode.assert_called_with(self.BEARER_TOKEN, None, None)

    def test_reverse_geocode__should_call_controller_with_none_when_lat_not_a_float(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(path='/geocode/reverse?latitude=abc&longitude=-93.6', headers=self.HEADERS)
        self.ctx.push()
        mock_controller.reverse_geocode.return_value = {}
        reverse_geocode()
        mock_controller.reverse_geocode.assert_called_with(self.BEARER_TOKEN, None, -93.6)

    def test_reverse_geocode__should_return_success_status_code(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {'city': 'Des Moines', 'state': 'IA'}
        actual = reverse_geocode()
        assert actual.status_code == 200

    def test_reverse_geocode__should_return_content_type(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {'city': 'Des Moines', 'state': 'IA'}
        actual = reverse_geocode()
        assert actual.content_type == 'application/json'

    def test_reverse_geocode__should_return_controller_response(self, mock_controller):
        response = {'city': 'Des Moines', 'state': 'IA'}
        mock_controller.reverse_geocode.return_value = response
        actual = reverse_geocode()
        assert json.loads(actual.data) == response

    def test_reverse_geocode__should_return_empty_object_when_controller_returns_empty(self, mock_controller):
        mock_controller.reverse_geocode.return_value = {}
        actual = reverse_geocode()
        assert json.loads(actual.data) == {}
