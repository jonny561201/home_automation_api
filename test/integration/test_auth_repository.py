import uuid

import pytest
from sqlalchemy import delete
from werkzeug.exceptions import Unauthorized

from svc.db.models.user_information_model import UserInformation
from svc.db.repositories.credential_repository import CredentialRepository
from svc.db.repositories.database_base import DatabaseBase


class TestDbCredentialIntegration:
    FIRST = 'Jon'
    LAST = 'Test'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        with DatabaseBase() as database:
            database.session.add(self.USER)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_user_info__should_return_user_information(self):
        with CredentialRepository() as database:
            actual = database.get_user_info(self.USER_ID)

            assert actual['user_id'] == self.USER_ID
            assert actual['first_name'] == self.FIRST
            assert actual['last_name'] == self.LAST

    def test_get_user_info__should_raise_unauthorized_when_user_not_found(self):
        with pytest.raises(Unauthorized):
            with CredentialRepository() as database:
                missing_user_id = str(uuid.uuid4())
                database.get_user_info(missing_user_id)


class TestDbPasswordIntegration:
    USER_NAME = 'JonsUser'
    PASSWORD = 'BESTESTPASSWORDEVA'
    USER_ID = str(uuid.uuid4())
    USER_INFO = UserInformation(first_name='test', last_name='Tester', id=USER_ID)

    def setup_method(self):
        with DatabaseBase() as database:
            database.session.add(self.USER_INFO)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))


