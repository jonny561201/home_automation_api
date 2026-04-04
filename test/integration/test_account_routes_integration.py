import json
import uuid

import jwt
from sqlalchemy import delete, select

from db.models.user_information_model import UserDevices
from integration.integration_helpers import mock_jwks_token
from svc.db.models.user_information_model import UserInformation, ChildAccounts, UserPreference, Devices, DeviceType
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestAccountRoutesIntegration:
    USER_NAME = 'Jon Rocks'
    PASSWORD = 'SuperSafePassword'
    USER_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    CHILD_CRED_ID = str(uuid.uuid4())
    PARENT_USER_ID = str(uuid.uuid4())
    CHILD_EMAIL = 'blackened_widow@gmail.com'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADERS = {'Authorization': f'Bearer {self.TOKEN}', 'Content-Type': 'application/json'}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city='Atlanta')
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Dylan', last_name='Test')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)

        with DatabaseBase() as database:
            stmt = select(DeviceType).where(DeviceType.type == 'Thermostat')
            type = database.session.execute(stmt).scalars().first()
            self.DEVICE = Devices(id=self.DEVICE_ID, node_name='test', node_device=1, ip_address='1.1.1.1', user_id=self.USER_ID, device_type_id=type.id)
            database.session.add(self.USER)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)
            database.session.add(self.USER_PREF)
            database.session.add(self.DEVICE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserDevices))
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(ChildAccounts))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))

    def test_post_child_account_by_user__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.post(f'account/createChildAccount', data='{}', headers={'Content-Type': 'application/json'})

        assert actual.status_code == 401

    def test_post_child_account_by_user__should_return_success_after_creating_child_account(self):
        post_body = json.dumps({'email': self.CHILD_EMAIL, 'deviceIds': [self.DEVICE_ID]})
        actual = self.TEST_CLIENT.post(f'account/createChildAccount', headers=self.HEADERS, data=post_body)

        assert actual.status_code == 200
        assert actual.json['email'] == self.CHILD_EMAIL

    def test_get_child_accounts_by_user_id__should_return_success_response(self):
        actual = self.TEST_CLIENT.get(f'account/childAccounts', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_get_child_accounts_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.get(f'account/childAccounts')

        assert actual.status_code == 401

    def test_delete_child_account_by_user_id__should_return_unauthorized_when_bad_jwt(self):
        actual = self.TEST_CLIENT.delete(f'account/childUserId/{self.CHILD_USER_ID}')

        assert actual.status_code == 401

    def test_delete_child_account_by_user_id__should_return_success_response(self):
        actual = self.TEST_CLIENT.delete(f'account/childUserId/{self.CHILD_USER_ID}', headers=self.HEADERS)

        assert actual.status_code == 200
