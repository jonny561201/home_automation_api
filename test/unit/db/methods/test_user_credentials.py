import uuid
from datetime import datetime, time

import pytest
from mock import mock, patch
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.db.methods.user_credentials import UserDatabase
from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel, Roles, UserInformation, UserRoles, RoleDevices, RoleDeviceNodes, ChildAccounts, ScheduleTasks


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
        preference_info = {'isFahrenheit': True, 'isImperial': True, 'city': 'Des Moines', 'lightAlarm': {}}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=user_id)

    def test_insert_preferences_by_user__should_raise_bad_request_when_preferences_empty(self):
        preference_info = {}
        user_id = uuid.uuid4()
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(user_id, preference_info)
            self.SESSION.query.return_value.filter_by.assert_not_called()

    def test_insert_preferences_by_user__should_not_throw_when_city_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_fahrenheit_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_imperial_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

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
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        self.SESSION.query.return_value.filter_by.assert_any_call(user_id=self.USER_ID)

    def test_add_new_role_device__should_query_user_role_id_by_child_user_id(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        parent_user_id = str(uuid.uuid4())
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        child_account = ChildAccounts(child_user_id=self.USER_ID, parent_user_id=parent_user_id)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = child_account
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        self.SESSION.query.return_value.filter_by.assert_any_call(user_id=parent_user_id)

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
        user_info = UserInformation()
        self.SESSION.query.return_value.filter_by.return_value.first.side_effect = [None, UserCredentials(user=user_info), UserPreference()]
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.query.return_value.filter_by.assert_any_call(user_id=self.USER_ID)

    @patch('svc.db.methods.user_credentials.UserCredentials')
    def test_create_child_account__should_update_the_user_id_and_insert_user(self, mock_user):
        user_info = UserInformation()
        new_user = UserCredentials()
        mock_user.return_value = new_user
        self.SESSION.query.return_value.filter_by.return_value.first.side_effect = [None, UserCredentials(user=user_info), UserPreference(), UserCredentials()]
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(new_user)

    @patch('svc.db.methods.user_credentials.UserInformation')
    def test_create_child_account__should_insert_user_info(self, mock_info):
        new_info = UserInformation()
        mock_info.return_value = new_info
        self.SESSION.query.return_value.filter_by.return_value.first.side_effect = [None, UserCredentials(user=UserInformation()), UserPreference()]
        self.DATABASE.create_child_account(self.USER_ID, "", [], self.FAKE_PASS)

        self.SESSION.add.assert_any_call(new_info)

    @patch('svc.db.methods.user_credentials.UserRoles')
    def test_create_child_account__should_insert_user_role(self, mock_roles):
        role = Roles(role_name='security')
        user_role = UserRoles(role=role)
        mock_roles.return_value = user_role
        self.SESSION.query.return_value.filter_by.return_value.first.side_effect = [None, UserCredentials(user=UserInformation(), user_roles=[user_role]), UserPreference(), UserCredentials()]
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
        self.SESSION.query.return_value.filter_by.return_value.first.side_effect = [None, creds, UserPreference(), creds]
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [account]

        actual = self.DATABASE.create_child_account(self.USER_ID, user_name, [], self.FAKE_PASS)
        assert actual == [{'user_name': user_name, 'user_id': user_id, 'roles': [role_name]}]

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

    def test_get_user_child_accounts__should_return_user_name_and_roles_per_user(self):
        user_id = uuid.uuid4()
        role_name = 'test_role'
        user_name = 'im_a_test_user'
        account = ChildAccounts(child_user_id=user_id)
        role = Roles(role_name=role_name)
        user_roles = UserRoles(role=role)
        creds = UserCredentials(user_roles=[user_roles], user_name=user_name)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [account]
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = creds
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == [{'user_name': user_name, 'user_id': user_id, 'roles': [role_name]}]

    def test_get_user_child_accounts__should_return_empty_list_when_no_child_accounts(self):
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = None
        actual = self.DATABASE.get_user_child_accounts(self.USER_ID)

        assert actual == []

    def test_delete_child_user_account__should_query_child_accounts_by_user_id(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [child_account]
        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)
        self.SESSION.query.assert_any_call(ChildAccounts)
        self.SESSION.query.return_value.filter_by.assert_any_call(parent_user_id=self.USER_ID, child_user_id=child_user_id)

    def test_delete_child_user_account__should_filter_user_account_by_child_user_id(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [child_account]

        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)

        self.SESSION.query.assert_called_with(UserCredentials)
        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=child_user_id)

    def test_delete_child_user_account__should_delete_child_account_relationship(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [child_account]

        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)

        self.SESSION.query.return_value.filter_by.return_value.delete.assert_called()

    def test_delete_child_user_account__should_try_to_delete_child_user_account(self):
        child_user_id = str(uuid.uuid4())
        child_account = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=child_user_id)
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [child_account]

        self.DATABASE.delete_child_user_account(self.USER_ID, child_user_id)

        self.SESSION.query.assert_called_with(UserCredentials)
        self.SESSION.query.return_value.filter_by.return_value.delete.assert_called()

    @patch('svc.db.methods.user_credentials.ScheduleTasks')
    def test_insert_schedule_task_by_user__should_call_add_with_task_settings(self, mock_tasks):
        task = {'alarmLightGroup': '1', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon'}
        created_task = ScheduleTasks()
        mock_tasks.return_value = created_task
        self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)

        self.SESSION.add.assert_called_with(created_task)

    def test_insert_schedule_task_by_user__should_return_query_response_with_task_id(self):
        task = {'alarmLightGroup': '1', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon'}
        task_id = uuid.uuid4()
        new_task = ScheduleTasks(id=task_id, alarm_light_group='1', alarm_time=time.fromisoformat('00:01:01'), alarm_days='Mon', alarm_group_name='bathroom')
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [new_task]
        actual = self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)

        assert actual[0]['task_id'] == str(task_id)

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_alarm_light_group_missing(self):
        preference_info = {'alarmDays': 'mon', 'alarmGroupName': 'bedroom', 'alarmTime': '00:01:00'}
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(self.USER_ID, preference_info)

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_alarm_time_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmDays': 'Mon'}
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(self.USER_ID, preference_info)

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_alarm_days_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00'}
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(self.USER_ID, preference_info)

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_alarm_light_name_missing(self):
        preference_info = {'alarmDays': 'mon', 'alarmLightGroup': '1', 'alarmTime': '00:01:00'}
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(self.USER_ID, preference_info)

    def test_get_schedule_tasks_by_user__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_schedule_tasks_by_user(None)

    def test_get_schedule_tasks_by_user__should_query_database_for_tasks(self):
        self.DATABASE.get_schedule_tasks_by_user(self.USER_ID)
        self.SESSION.query.assert_called_with(ScheduleTasks)
        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID)
        self.SESSION.query.return_value.filter_by.return_value.all.assert_called()

    def test_get_schedule_tasks_by_user_id__should_return_query_response(self):
        days = 'Sat'
        group_id = '1'
        group_name = 'Bedroom'
        group_time = '06:45:00'
        id = str(uuid.uuid4())
        task = ScheduleTasks(user_id=self.USER_ID, id=id, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID)

        assert actual[0]['alarm_group_name'] == group_name
        assert actual[0]['alarm_light_group'] == group_id
        assert actual[0]['alarm_days'] == days
        assert actual[0]['alarm_time'] == group_time
        assert actual[0]['task_id'] == id

    def test_update_schedule_task_by_user_id__should_query_for_user(self):
        task_id = 'asd123'
        task = {'taskId': task_id, 'alarmLightGroup': '1', 'alarmGroupName': 'jkasdhj', 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        self.SESSION.query.assert_called_with(ScheduleTasks)
        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID, id=task_id)
        self.SESSION.query.return_value.filter_by.return_value.first.assert_called()

    @patch('svc.db.methods.user_credentials.uuid')
    def test_update_schedule_task_by_user_id__should_update_task_id(self, mock_uuid):
        task_id = 'asd123'
        task = {'taskId': task_id, 'alarmLightGroup': '1', 'alarmGroupName': 'asdf', 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        new_task_id = uuid.uuid4()
        mock_uuid.uuid4.return_value = new_task_id
        existing_task = ScheduleTasks(user_id=self.USER_ID)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.user_id == self.USER_ID
        assert existing_task.id == str(new_task_id)

    def test_update_schedule_task_by_user_id__should_update_task_group_id(self):
        new_group_id = '1'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': new_group_id, 'alarmGroupName': 'test', 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_light_group='2')
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_light_group == new_group_id

    def test_update_schedule_task_by_user_id__should_update_task_group_name(self):
        group_name = 'doorwell'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': group_name, 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_group_name='potty')
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_group_name == group_name

    def test_update_schedule_task_by_user_id__should_update_task_days(self):
        days = 'MonTue'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': days, 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_days='Wed')
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_days == days

    def test_update_schedule_task_by_user_id__should_update_task_time_as_date_object(self):
        alarm_time = '00:00:00'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': alarm_time}
        existing_task = ScheduleTasks(alarm_light_group=time())
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_time == time.fromisoformat(alarm_time)

    def test_update_schedule_task_by_user_id__should_use_the_original_light_group_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': '00:00:00'}
        group_id = '2'
        existing_task = ScheduleTasks(alarm_light_group=group_id)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_light_group == group_id

    def test_update_schedule_task_by_user_id__should_use_the_original_light_group_name_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmDays': 'Mon', 'alarmTime': '00:00:00'}
        room = 'potty'
        existing_task = ScheduleTasks(alarm_group_name=room)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_group_name == room

    def test_update_schedule_task_by_user_id__should_use_the_original_light_alarm_days_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmLightGroup': '3', 'alarmTime': '00:00:00'}
        days = 'SatSun'
        existing_task = ScheduleTasks(alarm_days=days)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_days == days

    def test_update_schedule_task_by_user_id__should_use_the_original_light_time_days_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmLightGroup': '3'}
        alarm_time = time()
        existing_task = ScheduleTasks(alarm_time=alarm_time)
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_time == alarm_time

    def test_update_schedule_task_by_user_id__should_raise_exception_when_query_returns_zero_records(self):
        task = {'task_id': 'absdf'}
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

    def test_delete_schedule_task_by_user__should_query_for_existing_record(self):
        task_id = str(uuid.uuid4())
        self.DATABASE.delete_schedule_task_by_user(self.USER_ID, task_id)
        self.SESSION.query.assert_called_with(ScheduleTasks)
        self.SESSION.query.return_value.filter_by.assert_called_with(user_id=self.USER_ID, id=task_id)

    def test_delete_schedule_task_by_user__should_try_to_delete_record(self):
        task_id = str(uuid.uuid4())
        self.DATABASE.delete_schedule_task_by_user(self.USER_ID, task_id)
        self.SESSION.query.return_value.filter_by.return_value.delete.assert_called()

    @staticmethod
    def __create_user_preference(user, city='Moline', is_fahrenheit=False, is_imperial=False):
        preference = UserPreference()
        preference.user = user
        preference.city = city
        preference.is_fahrenheit = is_fahrenheit
        preference.is_imperial = is_imperial
        preference.alarm_light_group = '2'
        preference.alarm_time = datetime.now().time()
        preference.alarm_days = 'MonTueWedThuFri'
        preference.alarm_group_name = 'bedroom'

        return preference

    @staticmethod
    def __create_database_user(password=FAKE_PASS, first=FIRST_NAME, last=LAST_NAME):
        user = UserInformation(first_name=first, last_name=last)
        return UserCredentials(id=uuid.uuid4(), user_name=user, password=password, user=user)
