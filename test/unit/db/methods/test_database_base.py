import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from mock import mock
from sqlalchemy import orm
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import (UserPreference, UserCredentials, UserInformation)
from svc.db.repositories.database_base import DatabaseBase


class TestDatabaseBase:
    FAKE_USER = 'testName'
    FAKE_PASS = 'testPass'
    ROLE_NAME = 'garage_door'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'
    ROLE_ID = 'dcba4321'
    SESSION = None
    DATABASE = None
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = DatabaseBase()
        self.DATABASE.session = self.SESSION

    def test_get_preferences_by_user__should_return_user_temp_preferences(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit is 'celsius'

    def test_get_preferences_by_user__should_return_user_temp_preferences_with_fahrenheit(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, is_fahrenheit=True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit is 'fahrenheit'

    def test_get_preferences_by_user__should_return_user_city_preferences(self):
        city = 'London'
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, city)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.city == city

    def test_get_preferences_by_user__should_return_is_fahrenheit_preferences(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.isFahrenheit is True

    def test_get_preferences_by_user__should_return_is_imperial_preferences(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True, True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.isImperial is True

    def test_get_preferences_by_user__should_return_measure_unit_preferences(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True, True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.measureUnit == 'imperial'

    def test_get_preferences_by_user__should_return_measure_unit_preferences_for_metric(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.measureUnit == 'metric'

    def test_get_preferences_by_user__should_throw_not_found_when_no_preferences(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None

        with pytest.raises(NotFound):
            self.DATABASE.get_preferences_by_user(uuid.uuid4().hex)

    def test_get_preferences_by_user__should_throw_not_found_when_user_id_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_preferences_by_user(None)

        self.SESSION.execute.assert_not_called()

    def test_get_preferences_by_user__should_return_garage_id_state(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference
        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.garageId == 1

    def test_get_preferences_by_user__should_return_garage_door_state(self):
        user = TestDatabaseBase.__create_database_user()
        preference = TestDatabaseBase.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference
        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.garageDoor == 'Jons'

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
        preference.garage_id = 1
        preference.garage_door = 'Jons'

        return preference

    @staticmethod
    def __create_database_user(id=str(uuid.uuid4()), password=FAKE_PASS, first=FIRST_NAME, last=LAST_NAME):
        user = UserInformation(first_name=first, last_name=last)
        return UserCredentials(id=uuid.uuid4(), user_name=user, password=password, user=user, user_id=id)
