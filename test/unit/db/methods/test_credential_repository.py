import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import Unauthorized, NotFound

from svc.db.models.user_information_model import UserInformation
from svc.db.repositories.credential_repository import CredentialRepository


class TestCredentialRepository:
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = CredentialRepository()
        self.DATABASE.session = self.SESSION

    # def test_change_user_password__should_raise_bad_request_if_password_mismatch(self):
    #     user = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
    #     new_pass = 'newPass'
    #     self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
    #
    #     with pytest.raises(Unauthorized):
    #         self.DATABASE.change_user_password(self.FAKE_USER, self.FAKE_PASS, new_pass)
    #
    # def test_change_user_password__should_raise_not_found_if_user_id_none(self):
    #     with pytest.raises(NotFound):
    #         self.DATABASE.change_user_password(None, self.FAKE_PASS, 'some text')
    #     self.SESSION.query.assert_not_called()
    #
    # def test_change_user_password__should_make_update_call_when_credentials_match(self):
    #     new_pass = 'new_pass'
    #     user = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
    #     self.SESSION.execute.return_value.scalars.return_value.first.return_value = user
    #     self.DATABASE.change_user_password(self.FAKE_USER, self.FAKE_PASS, new_pass)
    #
    #     assert user.password == new_pass

    def test_get_user_info__should_return_the_matching_user_info(self):
        user = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.get_user_info(self.USER_ID)

        assert actual['user_id'] == self.USER_ID
        assert actual['first_name'] == self.FIRST_NAME
        assert actual['last_name'] == self.LAST_NAME

    def test_get_user_info__should_raise_unauthorized_if_user_is_none(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(Unauthorized):
            self.DATABASE.get_user_info('123abc')
