import uuid

import pytest
from sqlalchemy import delete, select
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import UserCredentials, UserInformation, Roles, UserRoles
from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.database_base import DatabaseBase


class TestAccountRepositoryIntegration:
    USER_ID = str(uuid.uuid4())
    CRED_ID = str(uuid.uuid4())
    LIGHTING_ROLE_ID = str(uuid.uuid4())
    GARAGE_ROLE_ID = str(uuid.uuid4())

    def setup_method(self):
        self.user = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.creds = UserCredentials(id=self.CRED_ID, user_name='test_user', password='pass', user_id=self.USER_ID)

        with DatabaseBase() as database:
            database.session.add(self.user)
            database.session.add(self.creds)
            database.session.commit()

            lighting_role = database.session.execute(select(Roles).filter_by(role_name='lighting')).scalars().first()
            garage_role = database.session.execute(select(Roles).filter_by(role_name='garage_door')).scalars().first()

            database.session.add(UserRoles(id=self.LIGHTING_ROLE_ID, user_id=self.USER_ID, role_id=lighting_role.id))
            database.session.add(UserRoles(id=self.GARAGE_ROLE_ID, user_id=self.USER_ID, role_id=garage_role.id))

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserRoles).where(UserRoles.id == self.LIGHTING_ROLE_ID))
            database.session.execute(delete(UserRoles).where(UserRoles.id == self.GARAGE_ROLE_ID))
            database.session.execute(delete(UserCredentials).where(UserCredentials.id == self.CRED_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_user_roles__should_return_role_names_as_strings(self):
        with AccountRepository() as database:
            actual = database.get_user_roles(self.USER_ID)

        assert sorted(actual.roles) == ['garage_door', 'lighting']

    def test_get_user_roles__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            with AccountRepository() as database:
                database.get_user_roles(None)

    def test_get_user_roles__should_raise_bad_request_when_user_not_found(self):
        with pytest.raises(BadRequest):
            with AccountRepository() as database:
                database.get_user_roles(str(uuid.uuid4()))
