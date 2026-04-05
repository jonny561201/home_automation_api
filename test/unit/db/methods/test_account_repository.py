import uuid

import mock
import pytest
from mock import patch
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest, NotFound

from svc.db.models.user_information_model import ChildAccounts, Devices, UserInformation, UserPreference
from svc.db.repositories.account_repository import AccountRepository


class TestAccountRepository:
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = AccountRepository()
        self.DATABASE.session = self.SESSION

    def test_get_user_child_accounts__should_return_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_user_child_accounts(None)
        self.SESSION.execute.assert_not_called()

    def test_get_user_child_accounts__should_return_user_name_and_roles_per_user(self):
        user_id = uuid.uuid4()
        account = ChildAccounts(child_user_id=user_id)
        user = UserInformation(id=user_id, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [account]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == [{'first_name': user.first_name, 'last_name': user.last_name, 'user_id': str(user_id), 'email': user.email}]

    def test_get_user_child_accounts__should_return_empty_list_when_no_child_accounts(self):
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = None
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == []

    def test_delete_child_user_account__should_raise_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.delete_child_user_account(None, str(uuid.uuid4()))
        self.SESSION.execute.assert_not_called()

    def test_delete_child_user_account__should_delete_child_account_relationship(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [child_account]

        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)

        self.SESSION.execute.assert_called()

    def test_create_child_account__should_raise_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.create_child_account(None, 'test@test.com', [])
        self.SESSION.execute.assert_not_called()

    def test_create_child_account__should_raise_bad_request_when_caller_is_child(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = ChildAccounts()
        with pytest.raises(BadRequest):
            self.DATABASE.create_child_account(self.USER_ID, 'test@test.com', [])

    def test_create_child_account__should_raise_not_found_when_parent_not_found(self):
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, None]
        with pytest.raises(NotFound):
            self.DATABASE.create_child_account(self.USER_ID, 'test@test.com', [])

    @patch('svc.db.repositories.account_repository.uuid')
    def test_create_child_account__should_return_new_child_info(self, mock_uuid):
        new_user_id = str(uuid.uuid4())
        email = 'child@test.com'
        mock_uuid.uuid4.return_value = new_user_id
        parent = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city='Des Moines')
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, parent, preference]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = []

        actual = self.DATABASE.create_child_account(self.USER_ID, email, [])

        assert actual == {'email': email, 'user_id': new_user_id}

    @patch('svc.db.repositories.account_repository.uuid')
    def test_create_child_account__should_add_user_info_preference_and_child_account(self, mock_uuid):
        new_user_id = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_user_id
        parent = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city='Des Moines')
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, parent, preference]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = []

        self.DATABASE.create_child_account(self.USER_ID, 'child@test.com', [])

        assert self.SESSION.add.call_count == 3

    @patch('svc.db.repositories.account_repository.uuid')
    def test_create_child_account__should_create_user_devices_for_each_matched_device(self, mock_uuid):
        new_user_id = str(uuid.uuid4())
        device_id_one = str(uuid.uuid4())
        device_id_two = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_user_id
        parent = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city='Des Moines')
        device_one = Devices(id=device_id_one, user_id=self.USER_ID)
        device_two = Devices(id=device_id_two, user_id=self.USER_ID)
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, parent, preference]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [device_one, device_two]

        self.DATABASE.create_child_account(self.USER_ID, 'child@test.com', [device_id_one, device_id_two])

        assert self.SESSION.add.call_count == 5

    @patch('svc.db.repositories.account_repository.uuid')
    def test_provision_user__should_add_user_to_session(self, mock_uuid):
        user_id = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = user_id
        self.DATABASE.provision_user(self.FIRST_NAME, self.LAST_NAME, 'test@test.com')

        self.SESSION.add.assert_called_once()

    @patch('svc.db.repositories.account_repository.uuid')
    def test_provision_user__should_return_generated_user_id(self, mock_uuid):
        user_id = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = user_id
        actual = self.DATABASE.provision_user(self.FIRST_NAME, self.LAST_NAME, 'test@test.com')

        assert actual == user_id