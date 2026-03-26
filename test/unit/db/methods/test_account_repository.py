import uuid

import mock
import pytest
from mock import patch
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest

from svc.db.repositories.account_repository import AccountRepository
from svc.db.models.user_information_model import ChildAccounts, Roles, UserRoles, UserCredentials, UserInformation, \
    UserPreference
from svc.models.account import UserRolesResponse


class TestAccountRepository:
    FAKE_PASS = 'testPass'
    ROLE_NAME = 'garage_door'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = AccountRepository()
        self.DATABASE.session = self.SESSION


    def test_get_user_child_accounts__should_return_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_child_accounts(None)
        self.SESSION.execute.assert_not_called()

    def test_get_user_child_accounts__should_return_user_name_and_roles_per_user(self):
        user_id = uuid.uuid4()
        role_name = 'test_role'
        user_name = 'im_a_test_user'
        account = ChildAccounts(child_user_id=user_id)
        role = Roles(role_name=role_name)
        user_roles = UserRoles(role=role)
        creds = UserCredentials(user_roles=[user_roles], user_name=user_name)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [account]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = creds
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == [{'user_name': user_name, 'user_id': str(user_id), 'roles': [role_name]}]

    def test_get_user_child_accounts__should_return_empty_list_when_no_child_accounts(self):
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = None
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == []

    def test_delete_child_user_account__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_child_user_account(None, str(uuid.uuid4()))
        self.SESSION.execute.assert_not_called()

    def test_delete_child_user_account__should_delete_child_account_relationship(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [child_account]

        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)

        self.SESSION.execute.assert_called()

    def test_create_child_account__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.create_child_account(None, '', [], '')
        self.SESSION.execute.assert_not_called()

    @patch('svc.db.repositories.account_repository.UserRoles')
    def test_create_child_account__should_insert_user_role(self, mock_roles):
        role = Roles(role_name='security')
        user_role = UserRoles(role=role)
        mock_roles.return_value = user_role
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, UserCredentials(user=UserInformation(), user_roles=[user_role]), UserPreference(), UserCredentials()]
        self.DATABASE.create_child_account(self.USER_ID, "", ['security'], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(user_role)

    def test_create_child_account__should_throw_bad_request_when_no_user(self):
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

    def test_create_child_account__should_return_list_of_child_accounts(self):
        user_id = uuid.uuid4()
        role_name = 'test_role'
        user_name = 'im_a_test_user'
        user_info = UserInformation()
        role = Roles(role_name=role_name)
        user_roles = UserRoles(role=role)
        account = ChildAccounts(child_user_id=user_id)
        creds = UserCredentials(user_roles=[user_roles], user_name=user_name, user=user_info)
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, creds, UserPreference(), creds]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [account]

        actual = self.DATABASE.create_child_account(self.USER_ID, user_name, [], self.FAKE_PASS)
        assert actual == [{'user_name': user_name, 'user_id': str(user_id), 'roles': [role_name]}]

    def test_get_roles_by_user__should_raise_bad_request_when_no_user(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_roles_by_user(self.USER_ID)

    def test_get_roles_by_user__should_raise_bad_request_when_no_user_id(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_roles_by_user(None)
        self.SESSION.execute.assert_not_called()

    def test_get_user_roles__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_roles(None)
        self.SESSION.execute.assert_not_called()

    def test_get_user_roles__should_raise_bad_request_when_user_not_found(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_roles(self.USER_ID)

    def test_get_user_roles__should_return_user_roles_response_with_role_names(self):
        role_one = Roles(role_name='lighting')
        role_two = Roles(role_name='security')
        user_roles = [UserRoles(role=role_one), UserRoles(role=role_two)]
        creds = UserCredentials(user_roles=user_roles)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = creds

        actual = self.DATABASE.get_user_roles(self.USER_ID)

        assert actual == UserRolesResponse(roles=['lighting', 'security'])

    def test_get_user_roles__should_return_empty_roles_when_user_has_none(self):
        creds = UserCredentials(user_roles=[])
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = creds

        actual = self.DATABASE.get_user_roles(self.USER_ID)

        assert actual == UserRolesResponse(roles=[])

    def test_insert_preferences_by_user__should_raise_bad_request_when_preferences_empty(self):
        preference_info = {}
        user_id = uuid.uuid4()
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(user_id, preference_info)
            self.SESSION.execute.return_value.scalars.assert_not_called()

    def test_insert_preferences_by_user__should_raise_bad_request_when_no_user_id(self):
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(None, {'isFahrenheit': True})
        self.SESSION.execute.assert_not_called()

    def test_insert_preferences_by_user__should_not_throw_when_city_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_fahrenheit_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_imperial_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_garage_door(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_garage_id(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    @staticmethod
    def __create_database_user(id=str(uuid.uuid4()), password=FAKE_PASS, first=FIRST_NAME, last=LAST_NAME):
        user = UserInformation(first_name=first, last_name=last)
        return UserCredentials(id=uuid.uuid4(), user_name=user, password=password, user=user, user_id=id)