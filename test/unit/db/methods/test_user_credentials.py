import uuid
from datetime import datetime

import pytest
from mock import mock, patch
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.db.methods.user_credentials import UserDatabase
from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel, Roles, UserInformation, UserRoles, RoleDevices, RoleDeviceNodes, ChildAccounts


class TestUserDatabase:
    FAKE_USER = 'testName'
    FAKE_PASS = 'testPass'
    ROLE_NAME = 'garage_door'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'
    ROLE_ID = 'dcba4321'
    SESSION = None
    DATABASE = None

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = UserDatabase(self.SESSION)

    def test_validate_credentials__should_query_database_by_user_name(self):
        user = self.__create_database_user()
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        self.SESSION.query.return_value.filter_by.assert_any_call(user_name=self.FAKE_USER)

    def test_validate_credentials__should_return_user_id_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['user_id'] == user.user_id

    def test_validate_credentials__should_return_roles_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        user.user_roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['roles'] == [{'role_name': self.ROLE_NAME }]

    def test_validate_credentials__should_return_first_name_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['first_name'] == self.FIRST_NAME

    def test_validate_credentials__should_return_last_name_if_password_matches_queried_user(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['last_name'] == self.LAST_NAME

    def test_validate_credentials__should_raise_unauthorized_if_password_does_not_match_queried_user(self):
        user = self.__create_database_user(password='mismatchedPass')
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

    def test_validate_credentials__should_raise_unauthorized_if_user_not_found(self):
        user = None
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

    def test_get_roles_by_user__should_query_user_creds_by_user_id(self):
        self.DATABASE.get_roles_by_user(self.USER_ID)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)

    def test_get_roles_by_user__should_raise_bad_request_when_no_user(self):
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_roles_by_user(self.USER_ID)

    def test_get_roles_by_user__should_return_the_user_roles(self):
        user = self.__create_database_user()
        user.user_id = '123455'
        user.user_roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['roles'] == [{'role_name': self.ROLE_NAME }]

    def test_get_preferences_by_user__should_return_user_temp_preferences(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['temp_unit'] is 'celsius'

    def test_get_preferences_by_user__should_return_user_temp_preferences_with_fahrenheit(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, is_fahrenheit=True)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['temp_unit'] is 'fahrenheit'

    def test_get_preferences_by_user__should_return_user_city_preferences(self):
        city = 'London'
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, city)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['city'] == city

    def test_get_preferences_by_user__should_return_is_fahrenheit_preferences(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, 'Fake City', True)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['is_fahrenheit'] is True

    def test_get_preferences_by_user__should_return_is_imperial_preferences(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, 'Fake City', True, True)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['is_imperial'] is True

    def test_get_preferences_by_user__should_return_measure_unit_preferences(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, 'Fake City', True, True)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['measure_unit'] == 'imperial'

    def test_get_preferences_by_user__should_return_measure_unit_preferences_for_metric(self):
        user = TestUserDatabase.__create_database_user()
        preference = TestUserDatabase.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual['measure_unit'] == 'metric'

    def test_get_preferences_by_user__should_throw_bad_request_when_no_preferences(self):
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(BadRequest):
            self.DATABASE.get_preferences_by_user(uuid.uuid4().hex)

    def test_insert_preferences_by_user__should_call_query(self):
        preference_info = {'isFahrenheit': True, 'isImperial': True, 'city': 'Des Moines'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=user_id)

    def test_insert_preferences_by_user__should_not_throw_when_city_missing(self):
        preference_info = {'isFahrenheit': False, 'isImperial': True}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_fahrenheit_missing(self):
        preference_info = {'city': 'London', 'isImperial': False}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_imperial_missing(self):
        preference_info = {'city': 'London', 'isFahrenheit': True}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_raise_bad_request_when_preferences_empty(self):
        preference_info = {}
        user_id = uuid.uuid4()
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(user_id, preference_info)
            self.SESSION.query.return_value.filter_by.assert_not_called()

    def test_get_current_sump_level_by_user__should_return_sump_levels(self):
        expected_distance = 43.9
        expected_warning = 1
        user = TestUserDatabase.__create_database_user()
        sump = DailySumpPumpLevel(user=user, distance=expected_distance, warning_level=expected_warning)
        self.SESSION.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = sump

        actual = self.DATABASE.get_current_sump_level_by_user(user.user_id)

        assert actual['currentDepth'] == expected_distance
        assert actual['warningLevel'] == expected_warning

    def test_get_current_sump_level_by_user__should_raise_bad_request_error_when_missing_record(self):
        self.SESSION.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_current_sump_level_by_user(uuid.uuid4().hex)

    def test_get_average_sump_level_by_user__should_return_sump_levels(self):
        expected_depth = 12.23
        user = TestUserDatabase.__create_database_user()
        date = datetime.date(datetime.now())
        average = AverageSumpPumpLevel(user=user, distance=expected_depth, create_day=date)
        self.SESSION.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = average

        actual = self.DATABASE.get_average_sump_level_by_user(user.user_id)

        assert actual['latestDate'] == str(date)
        assert actual['averageDepth'] == expected_depth

    def test_get_average_sump_level_by_user__should_raise_bad_request_error_when_no_records(self):
        self.SESSION.query.return_value.filter_by.return_value.order_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_average_sump_level_by_user('12345')

    def test_insert_current_sump_level__should_call_add(self):
        user_id = 1234
        depth_info = {'datetime': None,
                      'warning_level': 1,
                      'depth': None}
        self.DATABASE.insert_current_sump_level(user_id, depth_info)

        self.SESSION.add.assert_called()

    def test_insert_current_sump_level__should_raise_bad_request_when_depth_info_none(self):
        depth_info = None
        user_id = 1234
        with pytest.raises(BadRequest):
            self.DATABASE.insert_current_sump_level(user_id, depth_info)

    def test_insert_current_sump_level__should_raise_bad_request_when_depth_info_missing_keys(self):
        depth_info = {'badKey': 1234}
        user_id = 1234
        with pytest.raises(BadRequest):
            self.DATABASE.insert_current_sump_level(user_id, depth_info)

    def test_change_user_password__should_raise_bad_request_if_password_mismatch(self):
        user = self.__create_database_user(password='mismatched')
        new_pass = 'newPass'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user

        with pytest.raises(Unauthorized):
            self.DATABASE.change_user_password(self.FAKE_USER,self.FAKE_PASS, new_pass)

    def test_change_user_password__should_query_user_credentials(self):
        new_pass = 'new_pass'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = self.__create_database_user()
        self.DATABASE.change_user_password(self.USER_ID, self.FAKE_PASS, new_pass)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)

    def test_change_user_password__should_make_update_call_when_credentials_match(self):
        new_pass = 'new_pass'
        user = self.__create_database_user()
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.change_user_password(self.FAKE_USER, self.FAKE_PASS, new_pass)

        assert user.password == new_pass

    def test_add_new_role_device__should_call_add(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        self.SESSION.add.assert_called()

    def test_add_new_role_device__should_query_user_role_id_by_user_id(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)

    @patch('svc.db.methods.user_credentials.uuid')
    def test_add_new_role_device__should_return_device_id_in_response(self, mock_uuid):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        device_id = 'fake uuid string'
        mock_uuid.uuid4.return_value = device_id
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        actual = self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        assert actual == device_id

    def test_add_new_role_device__should_raise_unauthorized_when_no_role_returned(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name='security'))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        with pytest.raises(Unauthorized):
            self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

    def test_add_new_device_node__should_call_add(self):
        node_name = 'test name'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = devices
        self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name)

        self.SESSION.add.assert_called()

    def test_add_new_device_node__should_query_the_role_devices_by_role_id(self):
        node_name = 'test name'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = devices
        self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name)

        self.SESSION.query.return_value.filter_by.assert_called_with(id=self.ROLE_ID)

    def test_add_new_device_node__should_raise_unauthorized_when_device_id_not_match(self):
        node_name = 'test name'
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(Unauthorized):
            self.DATABASE.add_new_device_node(self.USER_ID, self.USER_ID, node_name)

    def test_add_new_device_node__should_return_the_number_of_node_positions_open(self):
        node_name = 'test name'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[])
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = devices
        actual = self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name)

        assert actual['availableNodes'] == 1

    def test_get_user_garage_ip__should_query_device_by_user_id(self):
        self.DATABASE.get_user_garage_ip(self.USER_ID)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)

    def test_get_user_garage_ip__should_raise_bad_request_error_when_no_user_role(self):
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_garage_ip(self.USER_ID)

    def test_get_user_garage_ip__should_return_ip_address_of_user(self):
        ip_address = '1.1.1.1'
        device = RoleDevices(ip_address=ip_address)
        role = UserRoles(user_id=self.USER_ID, role_devices=device, role=Roles(role_name='doesntMatter'))
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = role
        actual = self.DATABASE.get_user_garage_ip(self.USER_ID)

        assert actual == ip_address

    def test_create_child_account__should_query_user_creds_by_user_id(self):
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)

    def test_create_child_account__should_update_the_user_id_and_insert_user(self):
        user_roles = [UserRoles(role=Roles())]
        user = UserCredentials(user_id=str(uuid.uuid4()), user_name="test", user_roles=user_roles, user=UserInformation())
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(user)

    def test_create_child_account__should_insert_user_info(self):
        user_info = UserInformation()
        user = UserCredentials(user=user_info)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(user_info)

    def test_create_child_account__should_insert_user_role(self):
        user_info = UserInformation()
        role = Roles(role_name='security')
        user_role = UserRoles(role=role)
        user = UserCredentials(user=user_info, user_roles=[user_role])
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", ['security'], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(user_role)

    def test_create_child_account__should_filter_unwanted_roles_when_inserting(self):
        user_info = UserInformation()
        garage_role = Roles(role_name='garage_door')
        security_role = Roles(role_name='security')
        garage_user = UserRoles(role=garage_role)
        security_user = UserRoles(role=security_role)
        user = UserCredentials(user=user_info, user_roles=[garage_user, security_user])
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", ['garage_door'], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(garage_user)
        assert not mock.call(security_user) in self.SESSION.add.mock_calls

    def test_create_child_account__should_expunge_user(self):
        user_roles = [UserRoles(role=Roles())]
        user = UserCredentials(user_roles=user_roles, user=UserInformation())
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.expunge.assert_any_call(user)

    def test_create_child_account__should_expunge_user_role(self):
        role_name = 'GarageDoor'
        role = Roles(role_name=role_name)
        user_role = UserRoles(role=role)
        user = UserCredentials(user_roles=[user_role], user=UserInformation())
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", [role_name], self.FAKE_PASS)

        self.SESSION.expunge.assert_any_call(user_role)

    def test_create_child_account__should_expunge_user_info(self):
        user_info = UserInformation()
        user = UserCredentials(user=user_info)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.expunge.assert_any_call(user_info)

    def test_create_child_account__should_throw_bad_request_when_no_user(self):
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

    def test_get_user_child_accounts__should_query_children_accounts(self):
        self.DATABASE.get_user_child_accounts(self.USER_ID)
        self.SESSION.query.return_value.filter_by.assert_called_with(parent_user_id=self.USER_ID)

    def test_get_user_child_accounts__should_query_credentials_by_each_user_id(self):
        user_id_one = uuid.uuid4()
        user_id_two = uuid.uuid4()
        account_one = ChildAccounts(child_user_id=user_id_one)
        account_two = ChildAccounts(child_user_id=user_id_two)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [account_one, account_two]
        self.DATABASE.get_user_child_accounts(self.USER_ID)

        self.SESSION.query.return_value.filter_by.assert_any_call(user_id=user_id_one)
        self.SESSION.query.return_value.filter_by.assert_any_call(user_id=user_id_two)

    @staticmethod
    def __create_user_preference(user, city='Moline', is_fahrenheit=False, is_imperial=False):
        preference = UserPreference()
        preference.user = user
        preference.city = city
        preference.is_fahrenheit = is_fahrenheit
        preference.is_imperial = is_imperial

        return preference

    @staticmethod
    def __create_database_user(password=FAKE_PASS, first=FIRST_NAME, last=LAST_NAME):
        user = UserInformation(first_name=first, last_name=last)
        return UserCredentials(id=uuid.uuid4(), user_name=user, password=password, user=user)
