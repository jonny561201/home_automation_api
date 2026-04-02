import uuid

import pytest
from mock import patch
from sqlalchemy import delete, select
from werkzeug.exceptions import BadRequest, NotFound

from svc.db.models.user_information_model import UserCredentials, UserInformation, Roles, UserRoles, RoleDeviceNodes, \
    Devices, UserPreference, ChildAccounts
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

    def test_get_user_roles__should_raise_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            with AccountRepository() as database:
                database.get_user_roles(None)

    def test_get_user_roles__should_raise_not_found_when_user_not_found(self):
        with pytest.raises(NotFound):
            with AccountRepository() as database:
                database.get_user_roles(str(uuid.uuid4()))


@patch('svc.db.repositories.account_repository.uuid')
class TestAccountIntegration:
    PASSWORD = "Test"
    USER_NAME = "tony_stank  "
    ROLE_NAME = "Fake Lighting"
    CITY = 'Des Moines'
    GROUP_NAME = 'Bed Room'
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    CRED_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    UPDATED_USER_ID = uuid.uuid4()
    USER_ROLE_ID = str(uuid.uuid4())
    DEVICE_ID = str(uuid.uuid4())
    UPDATED_DEVICE_ID = str(uuid.uuid4())
    TEST_ROLE_ID = str(uuid.uuid4())

    def setup_method(self):
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="lighting", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID, role=self.ROLE)
        self.ROLE_DEVICE = Devices(user_role_id=self.USER_ROLE_ID, ip_address='0.0.0.0', max_nodes=1)
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        self.CHILD_USER = UserCredentials(id=str(uuid.uuid4()), user_name='Steve Rogers', password='', user_id=self.CHILD_USER_ID)
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)

        with DatabaseBase() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_LOGIN)
            database.session.add(self.USER_ROLE)
            database.session.add(self.ROLE_DEVICE)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == self.DEVICE_ID))
            database.session.execute(delete(Devices).where(Devices.user_role_id == self.USER_ROLE_ID))
            database.session.execute(delete(Devices).where(Devices.id == self.UPDATED_DEVICE_ID))

            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserRoles).where(UserRoles.user_id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserRoles).where(UserRoles.user_id == self.USER_ID))

            database.session.execute(delete(ChildAccounts))
            database.session.execute(delete(UserCredentials).where(UserCredentials.user_id == self.USER_ID))
            database.session.execute(delete(UserCredentials).where(UserCredentials.user_id == self.CHILD_USER_ID))
            database.session.execute(delete(UserCredentials).where(UserCredentials.user_id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserInformation).where(UserInformation.id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))
            database.session.execute(delete(Roles).where(Roles.id == self.ROLE_ID))
            database.session.execute(delete(Roles).where(Roles.id == self.TEST_ROLE_ID))

    def test_create_child_account__should_duplicate_existing_record(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4()]
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, new_email, [], self.PASSWORD)

            actual = database.session.execute(select(UserInformation).where(UserInformation.id == str(self.UPDATED_USER_ID))).scalars().first()
            assert actual.email == new_email
            assert str(actual.id) == str(self.UPDATED_USER_ID)

    def test_create_child_account__should_duplicate_existing_records_devices(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, new_email, [self.ROLE_NAME], self.PASSWORD)
            database.session.commit()

            actual = database.session.execute(select(UserRoles).where(UserRoles.user_id == str(self.UPDATED_USER_ID))).unique().scalars().all()
            lighting_role = next(x for x in actual if x.role.role_name == self.ROLE_NAME)
            assert lighting_role.role_devices.ip_address == '0.0.0.0'

    def test_create_child_account__should_not_duplicate_existing_records_devices_when_none_present(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            database.session.execute(delete(Devices).where(Devices.user_role_id == self.USER_ROLE_ID))

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, new_email, [self.ROLE_NAME], self.PASSWORD)
            database.session.commit()

            actual = database.session.execute(select(UserRoles).where(UserRoles.user_id == str(self.UPDATED_USER_ID))).unique().scalars().all()
            lighting_role = next(x for x in actual if x.role.role_name == self.ROLE_NAME)
            assert lighting_role.role_devices is None

    def test_create_child_account__should_reduce_roles(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'
        role_name = "security"
        role = Roles(id=self.TEST_ROLE_ID, role_desc=role_name, role_name=role_name)
        second_role = UserRoles(id=str(uuid.uuid4()), user_id=self.USER_ID, role_id=self.ROLE_ID, role=role)
        with AccountRepository() as database:
            database.session.add(second_role)
            database.session.commit()
            database.create_child_account(self.USER_ID, new_email, [role_name], self.PASSWORD)

            actual = database.session.execute(select(UserRoles).where(UserRoles.user_id == str(self.UPDATED_USER_ID))).unique().scalars().all()
            assert len(actual) == 1
            assert actual[0].role.role_name == role_name

    def test_create_child_account__should_throw_bad_request_when_no_user_exists(self, mock_uuid):
        with pytest.raises(BadRequest):
            with AccountRepository() as database:
                database.create_child_account(str(uuid.uuid4()), "", [], self.PASSWORD)

    def test_create_child_account__should_throw_bad_request_when_child_account(self, mock_uuid):
        with pytest.raises(BadRequest):
            user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
            with AccountRepository() as database:
                database.session.add(user)
                database.session.add(self.CHILD_USER)
                database.session.commit()
                database.session.add(self.CHILD_ACCOUNT)
                database.create_child_account(self.CHILD_USER_ID, "test@test.com", ['lighting'], self.PASSWORD)

    def test_create_child_account__should_create_preferences(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, self.USER_NAME, [self.ROLE_NAME], self.PASSWORD)

        with AccountRepository() as database:
            new_user = database.session.execute(select(UserPreference).where(UserPreference.user_id == str(self.UPDATED_USER_ID))).scalars().first()
            assert new_user.city == self.CITY
            assert new_user.is_fahrenheit is True
            assert new_user.is_imperial is True

    def test_create_child_account__should_create_child_account_record(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4()]
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            actual = database.create_child_account(self.USER_ID, new_email, [], self.PASSWORD)

            assert actual[0].get('user_name') == new_email
            assert actual[0].get('user_id') == str(self.UPDATED_USER_ID)
            assert actual[0].get('roles') == []

    def test_get_user_child_accounts__should_return_children_accounts(self, mock_uuid):
        user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with AccountRepository() as database:
            database.session.add(user)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

            actual = database.get_user_child_accounts(self.USER_ID)

            assert actual == [{'user_name': 'Steve Rogers', 'user_id': self.CHILD_USER_ID, 'roles': []}]

    def test_delete_child_user_account__should_remove_existing_child_account(self, mock_uuid):
        user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with AccountRepository() as database:
            database.session.add(user)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

        with AccountRepository() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with AccountRepository() as database:
            actual_child_account = database.session.execute(select(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_account is None
            actual_child_user = database.session.execute(select(UserCredentials).where(UserCredentials.user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_user is None

    def test_delete_child_user_account__should_not_delete_parent_when_no_child(self, mock_uuid):
        with AccountRepository() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with AccountRepository() as database:
            actual_child_account = database.session.execute(select(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_account is None
            actual_child_user = database.session.execute(select(UserCredentials).where(UserCredentials.user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_user is None
            actual_parent = database.session.execute(select(UserCredentials).where(UserCredentials.user_id == self.USER_ID)).scalars().first()
            assert actual_parent is not None

    def test_get_roles_by_user__should_return_role_device_data(self, mock_uuid):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        with AccountRepository() as database:
            database.session.execute(delete(Devices).where(Devices.user_role_id == self.USER_ROLE_ID))
            device = Devices(id=self.DEVICE_ID, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=self.DEVICE_ID, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            database.session.commit()
            actual = database.get_roles_by_user(self.USER_ID)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': self.DEVICE_ID,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_get_roles_by_user__should_raise_not_found_when_missing_user(self, mock_uuid):
        with pytest.raises(NotFound):
            with AccountRepository() as database:
                database.get_roles_by_user(str(uuid.uuid4()))
