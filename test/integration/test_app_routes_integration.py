import base64
import json
import os
import uuid

import jwt

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference, UserCredentials
from svc.manager import create_app


class TestAppRoutesIntegration:
    db_user = 'postgres'
    db_pass = 'password'
    db_port = '5432'
    db_name = 'garage_door'
    TEST_CLIENT = None
    JWT_SECRET = 'testSecret'
    USER_NAME = 'Jon Rocks'
    PASSWORD = 'SuperSafePassword'
    USER_ID = str(uuid.uuid4())
    CITY = 'Prague'
    USER = None
    USER_CRED = None
    PREFERENCE = None
    EMAIL_APP_ID = 'as;kljdfski;hasdf'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.db_user, 'SQL_PASSWORD': self.db_pass,
                           'SQL_DBNAME': self.db_name, 'SQL_PORT': self.db_port, 'EMAIL_APP_ID': self.EMAIL_APP_ID})
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.USER_CRED = UserCredentials(id=str(uuid.uuid4()), user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, city=self.CITY, is_fahrenheit=True, is_imperial=True)

        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_CRED)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.PREFERENCE)
            database.session.delete(self.USER_CRED)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')
        os.environ.pop('EMAIL_APP_ID')

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

    def test_update_user_password__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/updateAccount', data={}, headers=headers)

        assert actual.status_code == 401

    def test_update_user_password__should_update_user_password_successfully(self):
        new_pass = 'not important'
        post_body = json.dumps({'userName': self.USER_NAME, 'oldPassword': self.PASSWORD, 'newPassword': new_pass})
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/updateAccount', data=post_body, headers=headers)

        assert actual.status_code == 200

        with UserDatabaseManager() as database:
            creds = database.session.query(UserCredentials).filter_by(user_name=self.USER_NAME).first()
            assert creds.password == new_pass

    def test_get_roles_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.get('userId/%s/roles' % self.USER_ID)

        assert actual.status_code == 401

    def test_get_roles_by_user_id__should_return_success_response(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get('userId/%s/roles' % self.USER_ID, headers=headers)

        assert actual.status_code == 200
        assert json.loads(actual.data) == {'roles': []}

    def test_post_child_account_by_user__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.post('userId/%s/createChildAccount' % self.USER_ID)

        assert actual.status_code == 401

    def test_post_child_account_by_user__should_return_success_after_creating_child_account(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        post_body = json.dumps({'email': 'blackened_widow@gmail.com', 'roles': ['garage_door']})
        actual = self.TEST_CLIENT.post('userId/%s/createChildAccount' % self.USER_ID, headers=headers, data=post_body)

        assert actual.status_code == 200

