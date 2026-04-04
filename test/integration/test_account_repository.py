import uuid

import pytest
from mock import patch
from sqlalchemy import delete, select
from werkzeug.exceptions import BadRequest, NotFound

from svc.db.models.user_information_model import UserInformation, UserPreference, ChildAccounts, Devices, UserDevices, DeviceType
from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.database_base import DatabaseBase


@patch('svc.db.repositories.account_repository.uuid')
class TestAccountIntegration:
    USER_NAME = "tony_stank  "
    CITY = 'Des Moines'
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    UPDATED_USER_ID = uuid.uuid4()

    def setup_method(self):
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)

        with DatabaseBase() as database:
            database.session.add(self.USER_INFO)
            database.session.add(self.PREFERENCE)
            stmt = select(DeviceType).where(DeviceType.type == 'Garage Door')
            self.GARAGE_TYPE_ID = database.session.execute(stmt).scalars().first().id

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserDevices))
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(ChildAccounts))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserInformation).where(UserInformation.id == str(self.UPDATED_USER_ID)))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))

    def test_create_child_account__should_create_user_info_record(self, mock_uuid):
        mock_uuid.uuid4.return_value = self.UPDATED_USER_ID
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            actual = database.create_child_account(self.USER_ID, new_email, [])

            assert actual['email'] == new_email
            assert actual['user_id'] == str(self.UPDATED_USER_ID)

    def test_create_child_account__should_create_preferences(self, mock_uuid):
        mock_uuid.uuid4.return_value = self.UPDATED_USER_ID

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, 'tony_stank@stark.com', [])

        with AccountRepository() as database:
            new_pref = database.session.execute(select(UserPreference).where(UserPreference.user_id == str(self.UPDATED_USER_ID))).scalars().first()
            assert new_pref.city == self.CITY
            assert new_pref.is_fahrenheit is True
            assert new_pref.is_imperial is True

    def test_create_child_account__should_create_child_account_record(self, mock_uuid):
        mock_uuid.uuid4.return_value = self.UPDATED_USER_ID
        new_email = 'tony_stank@stark.com'

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, new_email, [])

        with AccountRepository() as database:
            child = database.session.execute(select(ChildAccounts).where(ChildAccounts.child_user_id == str(self.UPDATED_USER_ID))).scalars().first()
            assert child is not None
            assert str(child.parent_user_id) == self.USER_ID

    def test_create_child_account__should_create_user_devices_for_selected_devices(self, mock_uuid):
        mock_uuid.uuid4.return_value = self.UPDATED_USER_ID
        device_id = str(uuid.uuid4())
        with DatabaseBase() as database:
            device = Devices(id=device_id, user_id=self.USER_ID, ip_address='192.168.1.1', node_name='Left Garage', node_device=1, device_type_id=self.GARAGE_TYPE_ID)
            database.session.add(device)

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, 'tony_stank@stark.com', [device_id])

        with AccountRepository() as database:
            user_device = database.session.execute(select(UserDevices).where(UserDevices.user_id == str(self.UPDATED_USER_ID))).scalars().first()
            assert user_device is not None
            assert str(user_device.device_id) == device_id

    def test_create_child_account__should_not_create_user_devices_for_unowned_device_ids(self, mock_uuid):
        mock_uuid.uuid4.return_value = self.UPDATED_USER_ID
        unowned_device_id = str(uuid.uuid4())

        with AccountRepository() as database:
            database.create_child_account(self.USER_ID, 'tony_stank@stark.com', [unowned_device_id])

        with AccountRepository() as database:
            user_devices = database.session.execute(select(UserDevices).where(UserDevices.user_id == str(self.UPDATED_USER_ID))).scalars().all()
            assert user_devices == []

    def test_create_child_account__should_throw_bad_request_when_caller_is_child(self, mock_uuid):
        child_user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with AccountRepository() as database:
            database.session.add(child_user)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

        with pytest.raises(BadRequest):
            with AccountRepository() as database:
                database.create_child_account(self.CHILD_USER_ID, 'test@test.com', [])

    def test_create_child_account__should_throw_not_found_when_parent_not_found(self, mock_uuid):
        with pytest.raises(NotFound):
            with AccountRepository() as database:
                database.create_child_account(str(uuid.uuid4()), 'test@test.com', [])

    def test_get_user_child_accounts__should_return_children_accounts(self, mock_uuid):
        child_user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers', email='steve@test.com')
        with AccountRepository() as database:
            database.session.add(child_user)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

        with AccountRepository() as database:
            actual = database.get_user_child_accounts(self.USER_ID)

            assert actual == [{'first_name': 'Steve', 'last_name': 'Rogers', 'user_id': self.CHILD_USER_ID, 'email': 'steve@test.com'}]

    def test_delete_child_user_account__should_remove_existing_child_account(self, mock_uuid):
        device_id = str(uuid.uuid4())
        user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with AccountRepository() as database:
            database.session.add(user)
            device = Devices(id=device_id, user_id=self.USER_ID, ip_address='192.168.1.1', node_name='Left Garage', node_device=1, device_type_id=self.GARAGE_TYPE_ID)
            database.session.add(device)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)
            database.session.add(UserDevices(user_id=self.CHILD_USER_ID, device_id=device_id))

        with AccountRepository() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with AccountRepository() as database:
            actual_child_account = database.session.execute(select(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_account is None
            actual_child_user = database.session.execute(select(UserInformation).where(UserInformation.id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_user is not None
            actual_user_devices = database.session.execute(select(UserDevices).where(UserDevices.user_id == self.CHILD_USER_ID)).scalars().all()
            assert actual_user_devices == []

    def test_delete_child_user_account__should_not_delete_parent_when_no_child(self, mock_uuid):
        with AccountRepository() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with AccountRepository() as database:
            actual_child_account = database.session.execute(select(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_account is None
            actual_child_user = database.session.execute(select(UserInformation).where(UserInformation.id == self.CHILD_USER_ID)).scalars().first()
            assert actual_child_user is None
            actual_parent = database.session.execute(select(UserInformation).where(UserInformation.id == self.USER_ID)).scalars().first()
            assert actual_parent is not None
