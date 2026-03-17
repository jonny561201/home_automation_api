import json

import jwt
from flask import Flask, request
from mock import patch, ANY

from svc.models.thermostat import ThermostatState, DailyForecast
from svc.endpoints.thermostat_routes import get_temperature, set_temperature, get_forecast_data


@patch('svc.endpoints.thermostat_routes.thermostat_controller')
class TestThermostatRoutes:
    JWT_TOKEN = jwt.encode({}, 'JWT_SECRET', algorithm='HS256')
    BEARER_TOKEN = "Bearer " + JWT_TOKEN
    USER_ID = 'test'

    def setup_method(self):
        self.app = Flask(__name__)
        self.DAILY_FORECAST = DailyForecast(temp=12.0, minTemp=5.6, maxTemp=15.2, description='sunny')
        self.ctx = self.app.test_request_context(data=json.dumps({}), headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_get_temperature__should_call_thermostat_controller(self, mock_controller):
        get_temperature(self.USER_ID)

        mock_controller.get_user_temp.assert_called()

    def test_get_temperature__should_call_thermostat_controller_with_correct_parameters(self, mock_controller):
        get_temperature(self.USER_ID)

        mock_controller.get_user_temp.assert_called_with(self.USER_ID, self.BEARER_TOKEN)

    def test_get_temperature__should_return_response_from_controller(self, mock_controller):
        expected_temp = ThermostatState(currentTemp=12.0, isFahrenheit=False, minThermostatTemp=50.0, maxThermostatTemp=90.0, mode='test', desiredTemp=71.0)
        mock_controller.get_user_temp.return_value = expected_temp

        actual = get_temperature(self.USER_ID)

        assert json.loads(actual.data) == expected_temp.to_dict()

    def test_set_temperature__should_call_thermostat_controller(self, mock_controller):
        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called()

    def test_set_temperature__should_call_thermostat_controller_with_bearer_token(self, mock_controller):
        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called_with(ANY, self.BEARER_TOKEN)

    def test_set_temperature__should_call_thermostat_controller_with_request_body(self, mock_controller):
        request_data = json.dumps({'desiredTemp': 34.1}).encode()
        request.data = request_data

        set_temperature(self.USER_ID)

        mock_controller.set_user_temperature.assert_called_with(request_data, ANY)

    def test_get_forecast_data__should_call_thermostat_controller_with_user_id(self, mock_controller):
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(self.USER_ID, ANY)

    def test_get_forecast_data__should_call_thermostat_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(ANY, self.BEARER_TOKEN)

    def test_get_forecast_data__should_call_thermostat_controller_with_none_when_no_auth_header(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        get_forecast_data(self.USER_ID)
        mock_controller.get_user_forecast.assert_called_with(self.USER_ID, None)

    def test_get_forecast_data__should_return_success_response(self, mock_controller):
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        actual = get_forecast_data(self.USER_ID)
        assert actual.status_code == 200

    def test_get_forecast_data__should_return_success_headers(self, mock_controller):
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        actual = get_forecast_data(self.USER_ID)
        assert actual.content_type == 'application/json'

    def test_get_forecast_data__should_return_response_from_controller(self, mock_controller):
        mock_controller.get_user_forecast.return_value = self.DAILY_FORECAST
        actual = get_forecast_data(self.USER_ID)
        assert json.loads(actual.data) == self.DAILY_FORECAST.to_dict()
