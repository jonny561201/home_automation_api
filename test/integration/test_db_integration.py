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
    ROLE_ID = str(uuid.uuid4())
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'
    USER_NAME = 'Jonny'
    PASSWORD = 'fakePass'
    ROLE_NAME = 'garage_door'
    USER = None
    USER_LOGIN = None
    ROLE = None
    FIRST = 'Jon'
    LAST = 'Test'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        self.ROLE = Roles(role_name=self.ROLE_NAME, id=self.ROLE_ID, role_desc='doesnt matter')
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER)
            self.USER_LOGIN.role_id = database.session.query(Roles).first().id
            database.session.add(self.USER_LOGIN)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER)
            database.session.delete(self.USER_LOGIN)
            database.session.delete(self.ROLE)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_validate_credentials__should_return_user_id_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['user_id'] == self.USER_ID

    def test_validate_credentials__should_return_role_name_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['role_name'] == self.ROLE_NAME

    def test_validate_credentials__should_return_first_name_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['first_name'] == self.FIRST

    def test_validate_credentials__should_return_last_name_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['last_name'] == self.LAST

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
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_PREFERENCES)
            database.session.delete(self.USER)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

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
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'
    DEPTH = 8.0
    FIRST_USER_ID = str(uuid.uuid4())
    SECOND_USER_ID = str(uuid.uuid4())
    DAY = datetime.date(datetime.now())
    DATE = datetime.now()
    FIRST_USER = None
    SECOND_USER = None
    FIRST_SUMP_DAILY = None
    SECOND_SUMP_DAILY = None
    THIRD_SUMP_DAILY = None
    FIRST_SUMP_AVG = None
    SECOND_SUMP_AVG = None

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS,
                           'SQL_DBNAME': self.DB_NAME, 'SQL_PORT': self.DB_PORT})
        self.FIRST_USER = UserInformation(id=self.FIRST_USER_ID, first_name='Jon', last_name='Test')
        self.SECOND_USER = UserInformation(id=self.SECOND_USER_ID, first_name='Dylan', last_name='Fake')
        self.FIRST_SUMP_DAILY = DailySumpPumpLevel(id=88, distance=11.0, user_id=self.FIRST_USER_ID, warning_level=2, create_date=self.DATE)
        self.SECOND_SUMP_DAILY = DailySumpPumpLevel(id=99, distance=self.DEPTH, user_id=self.SECOND_USER_ID, warning_level=1, create_date=self.DATE)
        self.THIRD_SUMP_DAILY = DailySumpPumpLevel(id=100, distance=12.0, user_id=self.SECOND_USER_ID, warning_level=2, create_date=self.DATE)
        self.FIRST_SUMP_AVG = AverageSumpPumpLevel(id=34, user_id=self.FIRST_USER_ID, distance=12.0, create_day=self.DAY)
        self.SECOND_SUMP_AVG = AverageSumpPumpLevel(id=35, user_id=self.FIRST_USER_ID, distance=self.DEPTH, create_day=self.DAY)

        with UserDatabaseManager() as database:
            database.session.add_all([self.FIRST_USER, self.SECOND_USER])
            database.session.add_all([self.FIRST_SUMP_AVG, self.SECOND_SUMP_AVG])
            database.session.add_all([self.FIRST_SUMP_DAILY, self.SECOND_SUMP_DAILY, self.THIRD_SUMP_DAILY])

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.FIRST_SUMP_DAILY)
            database.session.delete(self.SECOND_SUMP_DAILY)
            database.session.delete(self.THIRD_SUMP_DAILY)
            database.session.delete(self.FIRST_SUMP_AVG)
            database.session.delete(self.SECOND_SUMP_AVG)
            database.session.delete(self.SECOND_USER)
            database.session.delete(self.FIRST_USER)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_current_sump_level_by_user__should_return_valid_sump_level(self):
        with UserDatabaseManager() as database:
            actual = database.get_current_sump_level_by_user(self.FIRST_USER_ID)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with UserDatabaseManager() as database:
            actual = database.get_current_sump_level_by_user(self.SECOND_USER_ID)
            assert actual['currentDepth'] == 12.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_raise_bad_request_when_user_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_current_sump_level_by_user(str(uuid.uuid4()))

    def test_get_average_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with UserDatabaseManager() as database:
            actual = database.get_average_sump_level_by_user(self.FIRST_USER_ID)
            assert actual == {'averageDepth': self.DEPTH, 'latestDate': str(self.DAY)}

    def test_get_average_sump_level_by_user__should_raise_bad_request_when_user_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_average_sump_level_by_user(str(uuid.uuid4()))

    def test_insert_current_sump_level__should_store_new_record(self):
        depth = 12.345
        with UserDatabaseManager() as database:
            depth_info = {'depth': depth,
                          'warning_level': 3,
                          'datetime': str(self.DATE)}
            database.insert_current_sump_level(self.FIRST_USER_ID, depth_info)

            actual = database.session.query(DailySumpPumpLevel).filter_by(user_id=self.FIRST_USER_ID, distance=depth).first()

            assert float(actual.distance) == depth

            database.session.query(DailySumpPumpLevel).filter_by(user_id=self.FIRST_USER_ID, distance=depth).delete()

    def test_insert_current_sump_level__should_raise_exception_with_bad_data(self):
        depth_info = {'badData': None}
        user_id = 1234
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                database.insert_current_sump_level(user_id, depth_info)
