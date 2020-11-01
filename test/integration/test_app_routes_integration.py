import base64
import json
import os
import uuid

import jwt

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.manager import create_app


class TestAppRoutesIntegration:
    db_user = 'postgres'
    db_pass = 'password'
    db_port = '5432'
    db_name = 'garage_door'
    JWT_SECRET = 'testSecret'
    USER_ID = str(uuid.uuid4())
    CITY = 'Prague'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.db_user, 'SQL_PASSWORD': self.db_pass, 'JWT_SECRET': self.JWT_SECRET,
                           'SQL_DBNAME': self.db_name, 'SQL_PORT': self.db_port})
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, city=self.CITY, is_fahrenheit=True, is_imperial=True)

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

    def test_health_check__should_return_success(self):
        actual = self.TEST_CLIENT.get('healthCheck')

        assert actual.status_code == 200
        assert actual.data.decode('UTF-8') == 'Success'

    def test_login__should_return_400_when_no_header(self):
        actual = self.TEST_CLIENT.get('login')

        assert actual.status_code == 400

    def test_login__should_return_401_when_invalid_user(self):
        user_name = 'not_real_user'
        user_pass = 'wrongPass'
        creds = "%s:%s" % (user_name, user_pass)
        headers = {'Authorization': base64.b64encode(creds.encode())}

        actual = self.TEST_CLIENT.get('login', headers=headers)

        assert actual.status_code == 401

    def test_login__should_return_401_when_invalid_password(self):
        user_name = 'Jonny561201'
        user_pass = 'wrongPass'
        creds = "%s:%s" % (user_name, user_pass)
        headers = {'Authorization': base64.b64encode(creds.encode())}

        actual = self.TEST_CLIENT.get('login', headers=headers)

        assert actual.status_code == 401

    def test_login__should_return_success_when_user_valid(self):
        user_name = 'Jonny561201'
        user_pass = 'password'
        creds = "%s:%s" % (user_name, user_pass)
        headers = {'Authorization': base64.b64encode(creds.encode())}

        actual = self.TEST_CLIENT.get('login', headers=headers)

        assert actual.status_code == 200

    def test_get_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('userId/' + self.USER_ID + '/preferences', headers=headers)

        assert actual.status_code == 401

    def test_get_user_preferences_by_user_id__should_return_success_when_valid_user(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get('userId/' + self.USER_ID + '/preferences', headers=headers)

        assert actual.status_code == 200
        assert json.loads(actual.data).get('city') == self.CITY

    def test_update_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/preferences/update', headers=headers)

        assert actual.status_code == 401

    def test_update_user_preferences_by_user_id__should_successfully_update_user(self):
        expected_city = 'Shannon'
        post_body = json.dumps({'city': expected_city, 'isFahrenheit': False})
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/preferences/update', data=post_body, headers=headers)

        assert actual.status_code == 200
        with UserDatabaseManager() as database:
            preference = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()
            assert preference.city == expected_city


