import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import Unauthorized, NotFound

from svc.db.models.user_information_model import UserInformation, UserCredentials, UserRoles, Roles
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