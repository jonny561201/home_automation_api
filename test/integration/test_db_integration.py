import os
import uuid
from datetime import datetime

import pytest
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, DailySumpPumpLevel, AverageSumpPumpLevel, \
    UserCredentials, Roles, UserPreference


class TestDbValidateIntegration:
    CRED_ID = str(uuid.uuid4())
    USER_ID = str(uuid.uuid4())
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'
    USER_NAME = 'Jonny'
    PASSWORD = 'fakePass'
    USER = None
    USER_LOGIN = None

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            self.USER_LOGIN.role_id = database.session.query(Roles).first().id
            database.session.add(self.USER_LOGIN)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER)
            database.session.delete(self.USER_LOGIN)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_validate_credentials__should_return_user_id_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual == self.USER_ID

    def test_validate_credentials__should_raise_unauthorized_when_user_does_not_exist(self):
        with UserDatabaseManager() as database:
            with pytest.raises(Unauthorized):
                database.validate_credentials('missingUser', 'missingPassword')

    def test_validate_credentials__should_raise_unauthorized_when_password_does_not_match(self):
        with UserDatabaseManager() as database:
            user_pass = 'wrongPassword'
            with pytest.raises(Unauthorized):
                database.validate_credentials(self.USER_NAME, user_pass)


class TestDbPreferenceIntegration:
    USER_ID = str(uuid.uuid4())
    CITY = 'Praha'
    UNIT = 'metric'
    USER = None
    USER_PREFERENCES = None

    def setup_method(self):
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_PREFERENCES)
            database.session.delete(self.USER)

    def test_get_preferences_by_user__should_return_preferences_for_valid_user(self):
        with UserDatabaseManager() as database:
            response = database.get_preferences_by_user(self.USER_ID)

            assert response['temp_unit'] == 'fahrenheit'
            assert response['measure_unit'] == 'imperial'
            assert response['city'] == self.CITY
            assert response['is_fahrenheit'] is True
            assert response['is_imperial'] is True

    def test_get_preferences_by_user__should_raise_bad_request_when_no_preferences(self):
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                bad_user_id = str(uuid.uuid4())
                database.get_preferences_by_user(bad_user_id)

    def test_insert_preferences_by_user__should_insert_valid_preferences(self):
        city = 'Vienna'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            database.session.commit()
            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True

    def test_insert_preferences_by_user__should_not_nullify_city_when_missing(self):
        preference_info = {'isFahrenheit': False, 'isImperial': True}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == self.CITY
            assert actual.is_fahrenheit is False
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_is_fahrenheit_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isImperial': False}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is False

    def test_insert_preferences_by_user__should_not_nullify_is_imperial_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True


class TestDbSumpIntegration:

    depth = 8.0
    first_user_id = str(uuid.uuid4())
    second_user_id = str(uuid.uuid4())
    day = datetime.date(datetime.now())
    date = datetime.now()
    first_user = None
    second_user = None
    first_sump_daily = None
    second_sump_daily = None
    third_sump_daily = None
    first_sump_average = None
    second_sump_average = None

    def setup_method(self):
        self.first_user = UserInformation(id=self.first_user_id, first_name='Jon', last_name='Test')
        self.second_user = UserInformation(id=self.second_user_id, first_name='Dylan', last_name='Fake')
        self.first_sump_daily = DailySumpPumpLevel(id=88, distance=11.0, user_id=self.first_user_id, warning_level=2, create_date=self.date)
        self.second_sump_daily = DailySumpPumpLevel(id=99, distance=self.depth, user_id=self.second_user_id, warning_level=1, create_date=self.date)
        self.third_sump_daily = DailySumpPumpLevel(id=100, distance=12.0, user_id=self.second_user_id, warning_level=2, create_date=self.date)
        self.first_sump_average = AverageSumpPumpLevel(id=34, user_id=self.first_user_id, distance=12.0, create_day=self.day)
        self.second_sump_average = AverageSumpPumpLevel(id=35, user_id=self.first_user_id, distance=self.depth, create_day=self.day)

        with UserDatabaseManager() as database:
            database.session.add_all([self.first_user, self.second_user])
            database.session.add_all([self.first_sump_average, self.second_sump_average])
            database.session.add_all([self.first_sump_daily, self.second_sump_daily, self.third_sump_daily])

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.first_sump_daily)
            database.session.delete(self.second_sump_daily)
            database.session.delete(self.third_sump_daily)
            database.session.delete(self.first_sump_average)
            database.session.delete(self.second_sump_average)
            database.session.delete(self.second_user)
            database.session.delete(self.first_user)

    def test_get_current_sump_level_by_user__should_return_valid_sump_level(self):
        with UserDatabaseManager() as database:
            actual = database.get_current_sump_level_by_user(self.first_user_id)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with UserDatabaseManager() as database:
            actual = database.get_current_sump_level_by_user(self.second_user_id)
            assert actual['currentDepth'] == 12.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_raise_bad_request_when_user_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_current_sump_level_by_user(str(uuid.uuid4()))

    def test_get_average_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with UserDatabaseManager() as database:
            actual = database.get_average_sump_level_by_user(self.first_user_id)
            assert actual == {'averageDepth': self.depth, 'latestDate': str(self.day)}

    def test_get_average_sump_level_by_user__should_raise_bad_request_when_user_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_average_sump_level_by_user(str(uuid.uuid4()))

    def test_insert_current_sump_level__should_store_new_record(self):
        depth = 12.345
        with UserDatabaseManager() as database:
            depth_info = {'depth': depth,
                          'warning_level': 3,
                          'datetime': str(self.date)}
            database.insert_current_sump_level(self.first_user_id, depth_info)

            actual = database.session.query(DailySumpPumpLevel).filter_by(user_id=self.first_user_id, distance=depth).first()

            assert float(actual.distance) == depth

            database.session.query(DailySumpPumpLevel).filter_by(user_id=self.first_user_id, distance=depth).delete()

    def test_insert_current_sump_level__should_raise_exception_with_bad_data(self):
        depth_info = {'badData': None}
        user_id = 1234
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                database.insert_current_sump_level(user_id, depth_info)
