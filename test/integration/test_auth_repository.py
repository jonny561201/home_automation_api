import datetime
import uuid
from zoneinfo import ZoneInfo

import pytest
from mock import patch
from sqlalchemy import delete, select
from werkzeug.exceptions import Unauthorized, Forbidden

from svc.db.models.user_information_model import RoleDevices, RoleDeviceNodes, UserCredentials, UserInformation, UserRoles, \
    Roles, RefreshToken
from svc.db.repositories.credential_repository import CredentialRepository
from svc.db.repositories.database_base import DatabaseBase


class TestDbCredentialIntegration:
    USER_NAME = 'Jonny'
    PASSWORD = 'fakePass'
    ROLE_NAME = 'garage_door'
    FIRST = 'Jon'
    LAST = 'Test'
    CRED_ID = str(uuid.uuid4())
    USER_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())

    def setup_method(self):
        self.ROLE = Roles(role_name=self.ROLE_NAME, id=self.ROLE_ID, role_desc='doesnt matter')
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, role_id=self.ROLE.id, user_id=self.USER_ID, role=self.ROLE)
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with DatabaseBase() as database:
            database.session.add(self.USER)
            self.USER_LOGIN.role_id = database.session.execute(select(Roles)).unique().scalars().first().id
            database.session.add(self.USER_LOGIN)
            database.session.add(self.USER_ROLE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == self.DEVICE_ID))
            database.session.execute(delete(RoleDevices).where(RoleDevices.id == self.DEVICE_ID))
            database.session.execute(delete(UserRoles).where(UserRoles.id == self.USER_ROLE_ID))
            database.session.execute(delete(Roles).where(Roles.id == self.ROLE_ID))
            database.session.execute(delete(UserCredentials).where(UserCredentials.id == self.CRED_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_validate_credentials__should_return_user_id_when_user_exists(self):
        with CredentialRepository() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['user_id'] == self.USER_ID

    def test_validate_credentials__should_return_first_name_when_user_exists(self):
        with CredentialRepository() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['first_name'] == self.FIRST

    def test_validate_credentials__should_return_last_name_when_user_exists(self):
        with CredentialRepository() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['last_name'] == self.LAST

    def test_validate_credentials__should_return_role_device_data(self):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        with CredentialRepository() as database:
            device = RoleDevices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=self.DEVICE_ID, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': self.DEVICE_ID,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_validate_credentials__should_raise_unauthorized_when_user_does_not_exist(self):
        with CredentialRepository() as database:
            with pytest.raises(Unauthorized):
                database.validate_credentials('missingUser', 'missingPassword')

    def test_validate_credentials__should_raise_unauthorized_when_password_does_not_match(self):
        with CredentialRepository() as database:
            user_pass = 'wrongPassword'
            with pytest.raises(Unauthorized):
                database.validate_credentials(self.USER_NAME, user_pass)

    def test_get_user_info__should_return_user_information(self):
        with CredentialRepository() as database:
            actual = database.get_user_info(self.USER_ID)

            assert actual['user_id'] == self.USER_ID
            assert actual['first_name'] == self.FIRST
            assert actual['last_name'] == self.LAST

    def test_get_user_info__should_return_role_device_data(self):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        with CredentialRepository() as database:
            device = RoleDevices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=self.DEVICE_ID, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            actual = database.get_user_info(self.USER_ID)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': self.DEVICE_ID,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_get_user_info__should_raise_unauthorized_when_user_not_found(self):
        with pytest.raises(Unauthorized):
            with CredentialRepository() as database:
                missing_user_id = str(uuid.uuid4())
                database.get_user_info(missing_user_id)


class TestRefreshTokenIntegration:
    FIRST = 'Kalynn'
    LAST = 'Graf'
    USER_ID = str(uuid.uuid4() )
    VALID_TOKEN = str(uuid.uuid4())
    WORN_TOKEN = str(uuid.uuid4())
    EXPIRED_TOKEN = str(uuid.uuid4())
    NOW = datetime.datetime.now(tz=ZoneInfo('US/Central'))
    EXPIRE = NOW + datetime.timedelta(hours=12)
    EXPIRED = NOW - datetime.timedelta(minutes=5)

    def setup_method(self):
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        self.VALID_REFRESH = RefreshToken(refresh=self.VALID_TOKEN, user_id=self.USER_ID, count=10, expire_time=self.EXPIRE)
        self.EXPIRED_REFRESH = RefreshToken(refresh=self.EXPIRED_TOKEN, user_id=self.USER_ID, count=10, expire_time=self.EXPIRED)
        self.WORN_REFRESH = RefreshToken(refresh=self.WORN_TOKEN, count=0, expire_time=self.EXPIRE)
        with DatabaseBase() as database:
            database.session.add(self.USER)
        with DatabaseBase() as database:
            database.session.add(self.EXPIRED_REFRESH)
            database.session.add(self.VALID_REFRESH)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(RefreshToken))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_insert_refresh_token__should_insert_token_to_db(self):
        token = str(uuid.uuid4())
        expire = self.NOW + datetime.timedelta(hours=12)
        with CredentialRepository() as database:
            database.insert_refresh_token(self.USER_ID, token, expire)

        with CredentialRepository() as database:
            stmt = select(RefreshToken).where(RefreshToken.refresh == token)
            actual = database.session.execute(stmt).scalars().first()
            assert actual.count == 10
            assert str(actual.user_id) == self.USER_ID
            assert str(actual.refresh) == token
            assert actual.expire_time == expire

    def test_insert_refresh_token__should_delete_existing_tokens_for_a_user(self):
        token = str(uuid.uuid4())
        expire = self.NOW + datetime.timedelta(hours=12)
        with CredentialRepository() as database:
            database.insert_refresh_token(self.USER_ID, token, expire)

        with CredentialRepository() as database:
            stmt = select(RefreshToken).where(RefreshToken.user_id == self.USER_ID)
            actual = database.session.execute(stmt).scalars().all()
            assert len(actual) == 1

    def test_generate_new_refresh_token__should_raise_forbidden_when_no_existing_refresh_token(self):
        missing_refresh = str(uuid.uuid4())
        with pytest.raises(Forbidden):
            with CredentialRepository() as database:
                database.generate_new_refresh_token(missing_refresh, self.NOW)

    def test_generate_new_refresh_token__should_raise_forbidden_when_token_has_expired(self):
        with pytest.raises(Forbidden):
            with CredentialRepository() as database:
                database.generate_new_refresh_token(self.EXPIRED_TOKEN, self.NOW)

    def test_generate_new_refresh_token__should_raise_forbidden_when_token_has_worn_out(self):
        with pytest.raises(Forbidden):
            with CredentialRepository() as database:
                database.generate_new_refresh_token(self.WORN_TOKEN, self.NOW)

    @patch('svc.db.repositories.credential_repository.uuid')
    def test_generate_new_refresh_token__should_return_a_valid_token(self, mock_uuid):
        new_refresh = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_refresh
        with CredentialRepository() as database:
            actual = database.generate_new_refresh_token(self.VALID_TOKEN, self.NOW)
            assert actual == {'user_id': self.USER_ID, 'refresh_token': new_refresh}


class TestDbPasswordIntegration:
    USER_NAME = 'JonsUser'
    PASSWORD = 'BESTESTPASSWORDEVA'
    USER_ID = str(uuid.uuid4())
    USER_CRED_ID = str(uuid.uuid4())

    def setup_method(self):
        self.USER_INFO = UserInformation(first_name='test', last_name='Tester', id=self.USER_ID)
        self.USER_CREDS = UserCredentials(id=self.USER_CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with DatabaseBase() as database:
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_CREDS)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserCredentials).where(UserCredentials.id == self.USER_CRED_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_change_user_password__should_raise_exception_with_mismatched_password(self):
        mismatched_pass = 'this wont match'
        new_pass = 'doesnt matter'
        with pytest.raises(Unauthorized):
            with CredentialRepository() as database:
                database.change_user_password(self.USER_ID, mismatched_pass, new_pass)

    def test_change_user_password__should_change_user_password_when_matching(self):
        new_pass = 'I SHOULD HAVE CHANGED!!!'
        with CredentialRepository() as database:
            database.change_user_password(self.USER_ID, self.PASSWORD, new_pass)

            user = database.session.execute(select(UserCredentials).where(UserCredentials.user_name == self.USER_NAME)).scalars().first()
            assert user.password == new_pass
