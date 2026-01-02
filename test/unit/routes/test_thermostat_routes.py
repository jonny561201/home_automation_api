import json

import jwt
from mock import patch, ANY

from svc.endpoints.thermostat_routes import get_temperature, set_temperature, get_forecast_data


@patch('svc.endpoints.thermostat_routes.request')
@patch('svc.endpoints.thermostat_routes.thermostat_controller')
class TestThermostatRoutes:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256').decode('UTF-8')
    BEARER_TOKEN = "Bearer " + JWT_TOKEN
    AUTH_HEADER = {"Authorization": BEARER_TOKEN}
    USER_ID = 'test'

    def test_get_temperature__should_call_thermostat_controller(self, mock_controller, mock_request):
        get_temperature(self.USER_ID)

        mock_controller.get_user_temp.assert_called()

    def test_get_temperature__should_call_thermostat_controller_with_correct_parameters(self, mock_controller, mock_request):
        mock_request.headers = self.AUTH_HEADER
        get_temperature(self.USER_ID)

        mock_controller.get_user_temp.assert_called_with(self.USER_ID, self.BEARER_TOKEN)

    def test_get_temperature__should_return_response_from_controller(self, mock_controller, mock_request):
        expected_temp = {'currentTemp': 34.12}
        mock_controller.get_user_temp.return_value = expected_temp

        actual = get_temperature(self.USER_ID)

        assert actual == expected_temp

    def test_set_temperature__should_call_thermostat_controller(self, mock_controller, mock_request):
        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called()

    def test_set_temperature__should_call_thermostat_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = self.AUTH_HEADER
        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called_with(ANY, self.BEARER_TOKEN)

    def test_set_temperature__should_call_thermostat_controller_with_request_body(self, mock_controller, mock_request):
        request = {'desiredTemp': 34.1}
        mock_request.data = request

        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called_with(request, ANY)

    def test_get_forecast_data__should_call_thermostat_controller_with_user_id(self, mock_controller, mock_request):
        mock_controller.get_user_forecast.return_value = {}
        mock_request.headers = self.AUTH_HEADER
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(self.USER_ID, ANY)

    def test_get_forecast_data__should_call_thermostat_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_controller.get_user_forecast.return_value = {}
        mock_request.headers = self.AUTH_HEADER
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(ANY, self.BEARER_TOKEN)

    def test_get_forecast_data__should_call_thermostat_controller_with_none_when_no_auth_header(self, mock_controller, mock_request):
        mock_controller.get_user_forecast.return_value = {}
        mock_request.headers = {}
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(self.USER_ID, None)

    def test_get_forecast_data__should_return_success_response(self, mock_controller, mock_request):
        mock_controller.get_user_forecast.return_value = {}
        actual = get_forecast_data(self.USER_ID)
        assert actual.status_code == 200

    def test_get_forecast_data__should_return_success_headers(self, mock_controller, mock_request):
        mock_controller.get_user_forecast.return_value = {}
        actual = get_forecast_data(self.USER_ID)
        assert actual.content_type == 'text/json'

    def test_get_forecast_data__should_return_response_from_controller(self, mock_controller, mock_request):
        response = {'myResponse': 'content'}
        mock_controller.get_user_forecast.return_value = response
        actual = get_forecast_data(self.USER_ID)
        assert json.loads(actual.data) == response
