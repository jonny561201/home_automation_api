import uuid

import jwt
import json
from mock import patch
from requests import Response
from sqlalchemy import delete

from svc.db.repositories.database_base import DatabaseBase
from svc.config.settings_state import Settings
from svc.constants.home_automation import Automation
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.manager import app


class TestThermostatRoutesIntegration:
    JWT_SECRET = 'fake_secret'
    USER_ID = str(uuid.uuid4())
    BEARER_TOKEN = jwt.encode({'sub': USER_ID}, JWT_SECRET, algorithm='HS256')
    HEADERS = {'Cookie': f'access_token={BEARER_TOKEN}', 'Content-Type': 'application/json'}

    def setup_method(self):
        Settings.get_instance()._settings = {'JwtSecret': self.JWT_SECRET}
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=str(self.USER_ID), city='London', is_fahrenheit=False, is_imperial=False)
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        with DatabaseBase() as database:
            database.session.add(self.USER)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_temperature__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.get('thermostat/temperature')

        assert actual.status_code == 401

    @patch('svc.controllers.thermostat_controller.get_desired_temp')
    @patch('svc.utilities.api_utils.requests')
    def test_get_temperature__should_return_temperature(self, mock_requests, mock_file):
        first = self._create_response(content={'results': [{'latitude': -93.1232, 'longitude': 12.323}]})
        second = self._create_response(content={'daily': {'temp': {'min': 21.0, 'max': 25.1}}})
        mock_file.return_value = {'desiredTemp': 22.2, 'mode': Automation.HVAC.MODE.HEATING}

        mock_requests.get.side_effect = [first, second]

        actual = self.TEST_CLIENT.get(f'thermostat/temperature', headers=self.HEADERS)

        assert actual.status_code == 200
        assert {'currentTemp', 'mode', 'minThermostatTemp', 'maxThermostatTemp', 'isFahrenheit', 'desiredTemp'} == set(json.loads(actual.data))

    def test_set_temperature__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.post('thermostat/temperature/desired', data='{}', headers={'Content-Type': 'application/json'})

        assert actual.status_code == 401

    @patch('svc.controllers.thermostat_controller.write_desired_temp_to_file')
    def test_set_temperature__should_return_successfully(self, mock_file):
        # bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        # headers = {'Authorization': bearer_token}
        request = {'desiredTemp': 23.7, 'mode': Automation.HVAC.MODE.HEATING, 'isFahrenheit': True}

        url = f'thermostat/temperature/desired'
        actual = self.TEST_CLIENT.post(url, data=json.dumps(request), headers=self.HEADERS)

        assert actual.status_code == 200

    def test_get_forecast_data__should_return_unauthorized_error_when_invalid_user(self):
        actual = self.TEST_CLIENT.get('thermostat/forecast')

        assert actual.status_code == 401

    @patch('svc.utilities.api_utils.requests')
    def test_get_forecast_data__should_return_successfully(self, mock_request):
        temp = 13.3
        min_temp = 22.0
        max_temp = 27.3
        first = self._create_response(content={'results': [{'latitude': 23.232, 'longitude': -93.232}]})
        second = self._create_response(content={'daily': {'temperature_2m_min': [min_temp], 'temperature_2m_max': [max_temp]}, 'current_weather': {'temperature': temp}})
        mock_request.get.side_effect = [first, second]

        actual = self.TEST_CLIENT.get(f'thermostat/forecast', headers=self.HEADERS)
        json_actual = json.loads(actual.data)

        assert actual.status_code == 200
        assert json_actual['minTemp'] == min_temp
        assert json_actual['maxTemp'] == max_temp
        assert json_actual['temp'] == temp

    @staticmethod
    def _create_response(status=200, content={}):
        response = Response()
        response.status_code = status
        response._content = json.dumps(content).encode()
        return response
