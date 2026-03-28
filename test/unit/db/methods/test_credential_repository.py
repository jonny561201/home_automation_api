import uuid
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import mock
import pytest
from mock import patch
from sqlalchemy import orm
from werkzeug.exceptions import Forbidden, Unauthorized, NotFound

from svc.db.models.user_information_model import RefreshToken, UserInformation, UserCredentials, UserRoles, Roles
from svc.db.repositories.credential_repository import CredentialRepository


class TestCredentialRepository:
    FAKE_USER = 'testName'
    FAKE_PASS = 'testPass'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    ROLE_NAME = 'garage_door'
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = CredentialRepository()
        self.DATABASE.session = self.SESSION

    def test_insert_refresh_token__should_call_add_method(self):
        refresh = str(uuid.uuid4())
        expire = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(hours=12)
        self.DATABASE.insert_refresh_token(self.USER_ID, refresh, expire)

        self.SESSION.add.assert_called()

    def test_generate_new_refresh_token__should_raise_unauthorized_if_token_does_not_exist(self):
        refresh = str(uuid.uuid4())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None

        with pytest.raises(Forbidden):
            self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

    def test_generate_new_refresh_token__should_raise_unauthorized_if_token_has_expired(self):
        refresh = str(uuid.uuid4())
        expired_token = RefreshToken()
        expired_token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) - timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = expired_token

        with pytest.raises(Forbidden):
            self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

    def test_generate_new_refresh_token__should_raise_unauthorized_token_count_has_expired(self):
        refresh = str(uuid.uuid4())
        expired_token = RefreshToken()
        expired_token.count = 0
        expired_token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = expired_token

        with pytest.raises(Forbidden):
            self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

    def test_generate_new_refresh_token__should_raise_unauthorized_token_count_is_below_zero(self):
        refresh = str(uuid.uuid4())
        expired_token = RefreshToken()
        expired_token.count = -1
        expired_token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = expired_token

        with pytest.raises(Forbidden):
            self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

    @patch('svc.db.repositories.credential_repository.uuid')
    def test_generate_new_refresh_token__should_return_a_new_refresh_token(self, mock_uuid):
        refresh = str(uuid.uuid4())
        new_refresh = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_refresh
        token = RefreshToken(user_id=self.USER_ID)
        token.count = 1
        token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = token

        actual = self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

        assert actual == {'user_id': self.USER_ID, 'refresh_token': new_refresh}

    @patch('svc.db.repositories.credential_repository.uuid')
    def test_generate_new_refresh_token__should_insert_new_refresh_token_into_db(self, mock_uuid):
        refresh = str(uuid.uuid4())
        new_refresh = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_refresh
        token = RefreshToken()
        token.count = 1
        token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = token

        self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

        assert token.refresh == new_refresh
        assert token.expire_time == self.NOW

    @patch('svc.db.repositories.credential_repository.uuid')
    def test_generate_new_refresh_token__should_reduce_refresh_count(self, mock_uuid):
        refresh = str(uuid.uuid4())
        new_refresh = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_refresh
        token = RefreshToken()
        token.count = 10
        token.expire_time = datetime.now(tz=ZoneInfo('US/Central')) + timedelta(minutes=1)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = token

        self.DATABASE.generate_new_refresh_token(refresh, self.NOW)

        assert token.count == 9

    def test_change_user_password__should_raise_bad_request_if_password_mismatch(self):
        user = self.__create_database_user(password='mismatched')
        new_pass = 'newPass'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.change_user_password(self.FAKE_USER, self.FAKE_PASS, new_pass)

    def test_change_user_password__should_raise_not_found_if_user_id_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.change_user_password(None, self.FAKE_PASS, 'some text')
        self.SESSION.query.assert_not_called()

    def test_change_user_password__should_make_update_call_when_credentials_match(self):
        new_pass = 'new_pass'
        user = self.__create_database_user()
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user
        self.DATABASE.change_user_password(self.FAKE_USER, self.FAKE_PASS, new_pass)

        assert user.password == new_pass

    def test_validate_credentials__should_return_the_user_roles(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        user.user_roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['roles'] == [{'role_name': self.ROLE_NAME }]

    def test_validate_credentials__should_return_user_id_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['user_id'] == user.user_id

    def test_validate_credentials__should_return_roles_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        user.user_roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['roles'] == [{'role_name': self.ROLE_NAME }]

    def test_validate_credentials__should_return_first_name_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['first_name'] == self.FIRST_NAME

    def test_validate_credentials__should_return_last_name_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['last_name'] == self.LAST_NAME

    def test_validate_credentials__should_raise_unauthorized_if_password_does_not_match_queried_user(self):
        user = self.__create_database_user(password='mismatchedPass')
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

    def test_validate_credentials__should_raise_unauthorized_if_user_not_found(self):
        user = None
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

    def test_get_user_info__should_return_the_matching_user_info(self):
        user_id = str(uuid.uuid4())
        user = self.__create_database_user(id=user_id, first=self.FIRST_NAME, last=self.LAST_NAME)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.get_user_info(user_id)

        assert actual['user_id'] == user_id
        assert actual['first_name'] == self.FIRST_NAME
        assert actual['last_name'] == self.LAST_NAME

    def test_get_user_info__should_return_roles_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        user.user_roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.get_user_info(user.user_id)

        assert actual['roles'] == [{'role_name': self.ROLE_NAME}]

    def test_get_user_info__should_raise_unauthorized_if_user_is_none(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(Unauthorized):
            self.DATABASE.get_user_info('123abc')

    @staticmethod
    def __create_database_user(id=str(uuid.uuid4()), password=FAKE_PASS, first=FIRST_NAME, last=LAST_NAME):
        user = UserInformation(first_name=first, last_name=last)
        return UserCredentials(id=uuid.uuid4(), user_name=user, password=password, user=user, user_id=id)