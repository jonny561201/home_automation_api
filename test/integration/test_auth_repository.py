import uuid

import pytest
from sqlalchemy import delete
from werkzeug.exceptions import Unauthorized

from svc.db.models.user_information_model import UserInformation
from svc.db.repositories.user_repository import UserRepository
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
        with UserRepository() as database:
            actual = database.get_user_info(self.USER_ID)

            assert actual['user_id'] == self.USER_ID
            assert actual['first_name'] == self.FIRST
            assert actual['last_name'] == self.LAST

    def test_get_user_info__should_raise_unauthorized_when_user_not_found(self):
        with pytest.raises(Unauthorized):
            with UserRepository() as database:
                missing_user_id = str(uuid.uuid4())
                database.get_user_info(missing_user_id)



