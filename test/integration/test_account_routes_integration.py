import json
import os
import uuid

import jwt
from sqlalchemy.orm.exc import ObjectDeletedError

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserCredentials, UserInformation, ChildAccounts, UserPreference
from svc.manager import app


class TestAccountRoutesIntegration:
    db_user = 'postgres'
    db_pass = 'password'
    db_port = '5432'
    db_name = 'garage_door'
    JWT_SECRET = 'testSecret'
    USER_NAME = 'Jon Rocks'
    PASSWORD = 'SuperSafePassword'
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    EMAIL_APP_ID = 'as;kljdfski;hasdf'

    def setup_method(self):
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        os.environ.update({'SQL_USERNAME': self.db_user, 'SQL_PASSWORD': self.db_pass, 'JWT_SECRET': self.JWT_SECRET,
                           'SQL_DBNAME': self.db_name, 'SQL_PORT': self.db_port, 'EMAIL_APP_ID': self.EMAIL_APP_ID})
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city='Atlanta')
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Dylan', last_name='Test')
        self.USER_CRED = UserCredentials(id=str(uuid.uuid4()), user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        self.CHILD_USER_CRED = UserCredentials(id=str(uuid.uuid4()), user_name='Steve Rogers', password='', user_id=self.CHILD_USER_ID)
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)

        with UserDatabaseManager() as database:
            database.session.add(self.USER_CRED)
            database.session.add(self.USER)
            database.session.add(self.CHILD_USER_CRED)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)
            database.session.add(self.USER_PREF)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(ChildAccounts).delete()
            database.session.delete(self.USER_PREF)
            # database.session.delete(self.USER)
            database.session.delete(self.USER_CRED)
            try:
                database.session.delete(self.CHILD_USER_CRED)
                # database.session.delete(self.CHILD_USER)

            except ObjectDeletedError:
                print('Child user credentials already deleted!Z')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')
        os.environ.pop('JWT_SECRET')
        os.environ.pop('EMAIL_APP_ID')

    def test_update_user_password__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('account/userId/' + self.USER_ID + '/updateAccount', data={}, headers=headers)

        assert actual.status_code == 401

    def test_update_user_password__should_update_user_password_successfully(self):
        new_pass = 'not important'
        post_body = json.dumps({'userName': self.USER_NAME, 'oldPassword': self.PASSWORD, 'newPassword': new_pass})
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post('account/userId/' + self.USER_ID + '/updateAccount', data=post_body, headers=headers)

        assert actual.status_code == 200

        with UserDatabaseManager() as database:
            creds = database.session.query(UserCredentials).filter_by(user_id=self.USER_ID).first()
            assert creds.password == new_pass

    def test_get_roles_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.get('account/userId/%s/roles' % self.USER_ID)

        assert actual.status_code == 401

    def test_get_roles_by_user_id__should_return_success_response(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get('account/userId/%s/roles' % self.USER_ID, headers=headers)

        assert actual.status_code == 200
        assert json.loads(actual.data) == {'roles': []}

    def test_post_child_account_by_user__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.post('account/userId/%s/createChildAccount' % self.USER_ID)

        assert actual.status_code == 401

    def test_post_child_account_by_user__should_return_success_after_creating_child_account(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        post_body = json.dumps({'email': 'blackened_widow@gmail.com', 'roles': ['garage_door']})
        actual = self.TEST_CLIENT.post('account/userId/%s/createChildAccount' % self.USER_ID, headers=headers, data=post_body)

        assert actual.status_code == 200

    def test_get_child_accounts_by_user_id__should_return_success_response(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get('account/userId/%s/childAccounts' % self.USER_ID, headers=headers)

        assert actual.status_code == 200

    def test_get_child_accounts_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.get('account/userId/%s/childAccounts' % self.USER_ID)

        assert actual.status_code == 401

    def test_delete_child_account_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.delete('account/userId/%s/childUserId/%s' % (self.USER_ID, self.CHILD_USER_ID))

        assert actual.status_code == 401

    def test_delete_child_account_by_user_id__should_return_success_response(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.delete('account/userId/%s/childUserId/%s' % (self.USER_ID, self.CHILD_USER_ID), headers=headers)

        assert actual.status_code == 200

