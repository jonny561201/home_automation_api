import os
import uuid

import jwt
from flask import json
from mock import patch
from requests import Response

from svc.constants.home_automation import Automation
from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.manager import app


class TestThermostatRoutesIntegration:
    TEST_CLIENT = None
    JWT_SECRET = 'fake_secret'
    USER_ID = None
    USER = None
    PREFERENCE = None
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'

    def setup_method(self):
        Settings.get_instance().dev_mode = False
        self.USER_ID = uuid.uuid4()
        self.USER = UserInformation(id=str(self.USER_ID), first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=str(self.USER_ID), city='London', is_fahrenheit=False, is_imperial=False)
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        os.environ.update({'JWT_SECRET': self.JWT_SECRET, 'SQL_USERNAME': self.DB_USER,
                           'SQL_PASSWORD': self.DB_PASS, 'SQL_DBNAME': self.DB_NAME,
                           'SQL_PORT': self.DB_PORT})
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.PREFERENCE)
            database.session.delete(self.USER)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_temperature__should_return_unauthorized_error_when_invalid_user(self):
        url = 'thermostat/temperature/' + '890234890234'
        actual = self.TEST_CLIENT.get(url)

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

        url = 'thermostat/temperature/' + str(self.USER_ID)
        actual = self.TEST_CLIENT.get(url, headers=headers)

        assert actual.status_code == 200
        assert {'currentTemp', 'mode', 'minThermostatTemp', 'maxThermostatTemp', 'isFahrenheit', 'desiredTemp'} == set(json.loads(actual.data))

    def test_set_temperature__should_return_unauthorized_error_when_invalid_user(self):
        url = 'thermostat/temperature/' + '3843040'
        actual = self.TEST_CLIENT.post(url)

        assert actual.status_code == 401

    @patch('svc.controllers.thermostat_controller.write_desired_temp_to_file')
    def test_set_temperature__should_return_successfully(self, mock_file):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        request = {'desiredTemp': 23.7, 'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': True}

        url = 'thermostat/temperature/' + str(self.USER_ID)
        actual = self.TEST_CLIENT.post(url, data=json.dumps(request), headers=headers)

        assert actual.status_code == 200

    def test_get_forecast_data__should_return_unauthorized_error_when_invalid_user(self):
        url = 'thermostat/forecast/3843040'
        actual = self.TEST_CLIENT.get(url)

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.requests')
    def test_get_forecast_data__should_return_successfully(self, mock_request):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        url = f'thermostat/forecast/{str(self.USER_ID)}'

        response_one = Response()
        response_two = Response()
        response_one.status_code = 200
        response_two.status_code = 200
        min_temp = 22.0
        max_temp = 27.3
        response_one._content = json.dumps({'daily': [{'temp': {'min': min_temp, 'max': max_temp}}]}).encode()
        response_two._content = json.dumps({'coord': {'lat': 23.232, 'lon': -93.232}}).encode()
        mock_request.get.side_effect = [response_two, response_one]

        actual = self.TEST_CLIENT.get(url, headers=headers)
        json_actual = json.loads(actual.data)

        assert actual.status_code == 200
        assert json_actual['minTemp'] == min_temp
        assert json_actual['maxTemp'] == max_temp

