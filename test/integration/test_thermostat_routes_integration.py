import os
import uuid

import jwt
from flask import json
from mock import patch

from svc.constants.home_automation import Automation
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.manager import create_app


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
        self.USER_ID = uuid.uuid4()
        self.USER = UserInformation(id=self.USER_ID.hex, first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=self.USER_ID.hex, city='London', is_fahrenheit=False, is_imperial=False)
        flask_app = create_app('__main__')
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

    # TODO: mock out call to weather api so it doesnt try to use env var
    def test_get_temperature__should_return_temperature(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        url = 'thermostat/temperature/' + self.USER_ID.hex
        actual = self.TEST_CLIENT.get(url, headers=headers)

        assert actual.status_code == 200
        assert {'currentTemp', 'mode', 'minThermostatTemp', 'maxThermostatTemp', 'isFahrenheit', 'description',
                'maxTemp', 'minTemp', 'temp', 'desiredTemp'} == set(json.loads(actual.data))

    def test_set_temperature__should_return_unauthorized_error_when_invalid_user(self):
        url = 'thermostat/temperature/' + '3843040'
        actual = self.TEST_CLIENT.post(url)

        assert actual.status_code == 401

    @patch('svc.utilities.event_utils.MyThread')
    def test_set_temperature__should_return_successfully(self, mock_thread):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        request = {'desiredTemp': 23.7, 'mode': Automation.MODE.HEATING, 'isFahrenheit': True}

        url = 'thermostat/temperature/' + str(self.USER_ID)
        actual = self.TEST_CLIENT.post(url, data=json.dumps(request), headers=headers)

        assert actual.status_code == 200

