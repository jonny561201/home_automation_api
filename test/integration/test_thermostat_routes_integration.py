import uuid

import jwt
from flask import json
from mock import patch
from requests import Response

from svc.config.settings_state import Settings
from svc.constants.home_automation import Automation
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.manager import app


class TestThermostatRoutesIntegration:
    JWT_SECRET = 'fake_secret'

    def setup_method(self):
        Settings.get_instance()._settings = {'JwtSecret': self.JWT_SECRET}
        self.USER_ID = uuid.uuid4()
        self.USER = UserInformation(id=str(self.USER_ID), first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=str(self.USER_ID), city='London', is_fahrenheit=False, is_imperial=False)
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.PREFERENCE)
            database.session.delete(self.USER)

    def test_get_temperature__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.get('thermostat/temperature/890234890234')

        assert actual.status_code == 401

    @patch('svc.controllers.thermostat_controller.get_desired_temp')
    @patch('svc.utilities.api_utils.requests')
    def test_get_temperature__should_return_temperature(self, mock_requests, mock_file):
        response_one = Response()
        response_one.status_code = 200
        response_one._content = json.dumps({'weather': [{'description': 'light drizzle'}],
                                        'main': {'temp': 23.4}}).encode()
        response_two = Response()
        response_two.status_code = 200
        response_two._content = json.dumps({'daily': [{'temp': {'min': 21.0, 'max': 25.1}}]}).encode()
        mock_file.return_value = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}

        mock_requests.get.side_effect = [response_two, response_one]
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'thermostat/temperature/{str(self.USER_ID)}', headers=headers)

        assert actual.status_code == 200
        assert {'currentTemp', 'mode', 'minThermostatTemp', 'maxThermostatTemp', 'isFahrenheit', 'desiredTemp'} == set(json.loads(actual.data))

    def test_set_temperature__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.post('thermostat/temperature/3843040')

        assert actual.status_code == 401

    @patch('svc.controllers.thermostat_controller.write_desired_temp_to_file')
    def test_set_temperature__should_return_successfully(self, mock_file):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        request = {'desiredTemp': 23.7, 'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': True}

        url = f'thermostat/temperature/{str(self.USER_ID)}'
        actual = self.TEST_CLIENT.post(url, data=json.dumps(request), headers=headers)

        assert actual.status_code == 200

    def test_get_forecast_data__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.get('thermostat/forecast/3843040')

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.requests')
    def test_get_forecast_data__should_return_successfully(self, mock_request):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        response_one = Response()
        response_two = Response()
        response_one.status_code = 200
        response_two.status_code = 200
        min_temp = 22.0
        max_temp = 27.3
        response_one._content = json.dumps({'daily': [{'temp': {'min': min_temp, 'max': max_temp}}]}).encode()
        response_two._content = json.dumps({'coord': {'lat': 23.232, 'lon': -93.232}}).encode()
        mock_request.get.side_effect = [response_two, response_one]

        actual = self.TEST_CLIENT.get(f'thermostat/forecast/{str(self.USER_ID)}', headers=headers)
        json_actual = json.loads(actual.data)

        assert actual.status_code == 200
        assert json_actual['minTemp'] == min_temp
        assert json_actual['maxTemp'] == max_temp

