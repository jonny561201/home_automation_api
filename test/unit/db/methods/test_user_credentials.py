import uuid
from datetime import datetime

import pytest
from mock import mock
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.db.methods.user_credentials import UserDatabase
from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel, Roles, UserInformation, UserRoles


class TestUserDatabase:
    FAKE_USER = 'testName'
    FAKE_PASS = 'testPass'
    ROLE_NAME = 'garage_door'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
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
        roles = [UserRoles(role=Roles(role_name=self.ROLE_NAME))]
        self.SESSION.query.return_value.filter_by.return_value.first.return_value = user
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = roles

        actual = self.DATABASE.validate_credentials(self.FAKE_USER, self.FAKE_PASS)

        assert actual['roles'] == [self.ROLE_NAME]

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
