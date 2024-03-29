import os
import uuid
import datetime

import pytest
import pytz
from mock import patch
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden

from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, DailySumpPumpLevel, AverageSumpPumpLevel, \
    UserCredentials, Roles, UserPreference, UserRoles, RoleDevices, RoleDeviceNodes, ChildAccounts, ScheduleTasks, \
    ScheduledTaskTypes, Scenes, SceneDetails, RefreshToken

DB_USER = 'postgres'
DB_PASS = 'password'
DB_PORT = '5432'
DB_NAME = 'garage_door'


class TestDbValidateIntegration:
    CRED_ID = str(uuid.uuid4())
    USER_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    USER_NAME = 'Jonny'
    PASSWORD = 'fakePass'
    ROLE_NAME = 'garage_door'
    FIRST = 'Jon'
    LAST = 'Test'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.ROLE = Roles(role_name=self.ROLE_NAME, id=str(uuid.uuid4()), role_desc='doesnt matter')
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, role_id=self.ROLE.id, user_id=self.USER_ID, role=self.ROLE)
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            self.USER_LOGIN.role_id = database.session.query(Roles).first().id
            database.session.add(self.USER_LOGIN)
            database.session.add(self.USER_ROLE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(RoleDeviceNodes).delete()
            database.session.query(RoleDevices).delete()
            database.session.delete(self.USER_LOGIN)
            database.session.commit()
            database.session.delete(self.ROLE)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_validate_credentials__should_return_user_id_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['user_id'] == self.USER_ID

    def test_validate_credentials__should_return_first_name_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['first_name'] == self.FIRST

    def test_validate_credentials__should_return_last_name_when_user_exists(self):
        with UserDatabaseManager() as database:
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['last_name'] == self.LAST

    def test_validate_credentials__should_return_role_device_data(self):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        device_id = str(uuid.uuid4())
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=device_id, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            actual = database.validate_credentials(self.USER_NAME, self.PASSWORD)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': device_id,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_validate_credentials__should_raise_unauthorized_when_user_does_not_exist(self):
        with UserDatabaseManager() as database:
            with pytest.raises(Unauthorized):
                database.validate_credentials('missingUser', 'missingPassword')

    def test_validate_credentials__should_raise_unauthorized_when_password_does_not_match(self):
        with UserDatabaseManager() as database:
            user_pass = 'wrongPassword'
            with pytest.raises(Unauthorized):
                database.validate_credentials(self.USER_NAME, user_pass)

    def test_get_user_info__should_return_user_information(self):
        with UserDatabaseManager() as database:
            actual = database.get_user_info(self.USER_ID)

            assert actual['user_id'] == self.USER_ID
            assert actual['first_name'] == self.FIRST
            assert actual['last_name'] == self.LAST

    def test_get_user_info__should_return_role_device_data(self):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        device_id = str(uuid.uuid4())
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=device_id, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            actual = database.get_user_info(self.USER_ID)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': device_id,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_get_user_info__should_raise_unauthorized_when_user_not_found(self):
        with pytest.raises(Unauthorized):
            with UserDatabaseManager() as database:
                missing_user_id = str(uuid.uuid4())
                database.get_user_info(missing_user_id)

    def test_get_roles_by_user__should_return_role_device_data(self):
        ip_address = '0.1.2.3'
        node_name = 'test_node'
        device_id = str(uuid.uuid4())
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=1, ip_address=ip_address)
            node = RoleDeviceNodes(role_device_id=device_id, node_name=node_name, node_device=1)
            database.session.add(device)
            database.session.add(node)
            actual = database.get_roles_by_user(self.USER_ID)

            assert actual['roles'] == [{'ip_address': ip_address, 'role_name': self.ROLE_NAME, 'device_id': device_id,
                                        'devices': [{'node_device': 1, 'node_name': node_name}]}]

    def test_get_roles_by_user__should_raise_bad_request_when_missing_user(self):
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                database.get_roles_by_user(str(uuid.uuid4()))


class TestRefreshTokenIntegration:
    FIRST = 'Kalynn'
    LAST = 'Graf'
    USER_ID = str(uuid.uuid4() )
    VALID_TOKEN = str(uuid.uuid4())
    WORN_TOKEN = str(uuid.uuid4())
    EXPIRED_TOKEN = str(uuid.uuid4())
    NOW = datetime.datetime.now(tz=pytz.timezone('US/Central'))
    EXPIRE = NOW + datetime.timedelta(hours=12)
    EXPIRED = NOW - datetime.timedelta(minutes=5)

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        self.VALID_REFRESH = RefreshToken(refresh=self.VALID_TOKEN, user_id=self.USER_ID, count=10, expire_time=self.EXPIRE)
        self.EXPIRED_REFRESH = RefreshToken(refresh=self.EXPIRED_TOKEN, user_id=self.USER_ID, count=10, expire_time=self.EXPIRED)
        self.WORN_REFRESH = RefreshToken(refresh=self.WORN_TOKEN, count=0, expire_time=self.EXPIRE)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
        with UserDatabaseManager() as database:
            database.session.add(self.EXPIRED_REFRESH)
            database.session.add(self.VALID_REFRESH)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(RefreshToken).delete()
            database.session.delete(self.USER)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_insert_refresh_token__should_insert_token_to_db(self):
        token = str(uuid.uuid4())
        expire = self.NOW + datetime.timedelta(hours=12)
        with UserDatabaseManager() as database:
            database.insert_refresh_token(self.USER_ID, token, expire)

        with UserDatabaseManager() as database:
            actual = database.session.query(RefreshToken).filter_by(refresh=token).first()
            assert actual.count == 10
            assert actual.user_id == self.USER_ID
            assert actual.refresh == token
            assert actual.expire_time == expire

    def test_insert_refresh_token__should_delete_existing_tokens_for_a_user(self):
        token = str(uuid.uuid4())
        expire = self.NOW + datetime.timedelta(hours=12)
        with UserDatabaseManager() as database:
            database.insert_refresh_token(self.USER_ID, token, expire)

        with UserDatabaseManager() as database:
            actual = database.session.query(RefreshToken).filter_by(user_id=self.USER_ID).all()
            assert len(actual) == 1

    def test_generate_new_refresh_token__should_raise_forbidden_when_no_existing_refresh_token(self):
        missing_refresh = str(uuid.uuid4())
        with pytest.raises(Forbidden):
            with UserDatabaseManager() as database:
                database.generate_new_refresh_token(missing_refresh, self.NOW)

    def test_generate_new_refresh_token__should_raise_forbidden_when_token_has_expired(self):
        with pytest.raises(Forbidden):
            with UserDatabaseManager() as database:
                database.generate_new_refresh_token(self.EXPIRED_TOKEN, self.NOW)

    def test_generate_new_refresh_token__should_raise_forbidden_when_token_has_worn_out(self):
        with pytest.raises(Forbidden):
            with UserDatabaseManager() as database:
                database.generate_new_refresh_token(self.WORN_TOKEN, self.NOW)

    @patch('svc.db.methods.user_credentials.uuid')
    def test_generate_new_refresh_token__should_return_a_valid_token(self, mock_uuid):
        new_refresh = str(uuid.uuid4())
        mock_uuid.uuid4.return_value = new_refresh
        with UserDatabaseManager() as database:
            actual = database.generate_new_refresh_token(self.VALID_TOKEN, self.NOW)
            assert actual == {'user_id': self.USER_ID, 'refresh_token': new_refresh}


class TestDbPreferenceIntegration:
    USER_ID = str(uuid.uuid4())
    TASK_ID = str(uuid.uuid4())
    TASK_NAME = 'all on'
    CITY = 'Praha'
    UNIT = 'metric'
    LIGHT_GROUP = '42'
    LIGHT_TIME = '02:22:22'
    GROUP_NAME = 'secret room'
    DAYS = 'MonTueWedThuFri'
    GARAGE = 'Jons'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.TASK = ScheduleTasks(user_id=self.USER_ID, id=self.TASK_ID, alarm_light_group=self.LIGHT_GROUP, alarm_group_name=self.GROUP_NAME, alarm_days=self.DAYS, alarm_time=datetime.time.fromisoformat(self.LIGHT_TIME), enabled=True)
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY, garage_door=self.GARAGE, garage_id=1)
        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(ScheduleTasks).delete()
            database.session.delete(self.USER_PREFERENCES)
            database.session.delete(self.USER)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_schedule_task_by_user__should_return_task(self):
        with UserDatabaseManager() as database:
            task_type = database.session.query(ScheduledTaskTypes).first()
            task_name = task_type.activity_name
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with UserDatabaseManager() as database:
            actual = database.get_schedule_tasks_by_user(self.USER_ID, None)
            assert actual[0]['alarm_light_group'] == self.LIGHT_GROUP
            assert actual[0]['alarm_group_name'] == self.GROUP_NAME
            assert actual[0]['alarm_days'] == self.DAYS
            assert actual[0]['alarm_time'] == self.LIGHT_TIME
            assert actual[0]['task_id'] == self.TASK_ID
            assert actual[0]['enabled'] == True
            assert actual[0]['task_type'] == task_name

    def test_get_schedule_task_by_user__should_return_empty_list_when_no_matches(self):
        user_id = str(uuid.uuid4())
        with UserDatabaseManager() as database:
            actual = database.get_schedule_tasks_by_user(user_id, None)
            assert actual == []

    def test_insert_schedule_task_by_user__should_insert_task(self):
        task = {'alarmTime': self.LIGHT_TIME, 'alarmLightGroup': self.LIGHT_GROUP, 'alarmGroupName': self.GROUP_NAME, 'alarmDays': self.DAYS, 'enabled': False, 'taskType': 'turn on'}
        with UserDatabaseManager() as database:
            database.insert_schedule_task_by_user(self.USER_ID, task)

        with UserDatabaseManager() as database:
            actual = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert actual.user_id == self.USER_ID
            assert actual.alarm_light_group == self.LIGHT_GROUP
            assert actual.alarm_time == datetime.time.fromisoformat(self.LIGHT_TIME)
            assert actual.alarm_days == self.DAYS
            assert actual.alarm_group_name == self.GROUP_NAME
            assert actual.enabled is False

    def test_insert_schedule_task_by_user__should_insert_task_for_all_rooms(self):
        task = {'alarmTime': self.LIGHT_TIME, 'alarmLightGroup': '0', 'alarmGroupName': self.GROUP_NAME, 'alarmDays': self.DAYS, 'enabled': False, 'taskType': 'turn on'}
        with UserDatabaseManager() as database:
            database.insert_schedule_task_by_user(self.USER_ID, task)

        with UserDatabaseManager() as database:
            actual = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert actual.user_id == self.USER_ID
            assert actual.alarm_light_group == '0'

    def test_delete_schedule_tasks_by_user__should_delete_record_that_already_exists(self):
        with UserDatabaseManager() as database:
            task_type = database.session.query(ScheduledTaskTypes).first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with UserDatabaseManager() as database:
            database.delete_schedule_task_by_user(self.USER_ID, self.TASK_ID)

        with UserDatabaseManager() as database:
            actual = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert actual is None

    def test_update_schedule_task_by_user__should_raise_bad_request_when_user_does_not_exist(self):
        new_task = {'taskId': str(uuid.uuid4()), 'alarmDays': 'SatSun', 'alarmGroupName': 'private potty room'}
        with UserDatabaseManager() as database:
            task_type = database.session.query(ScheduledTaskTypes).first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                database.update_schedule_task_by_user_id(self.USER_ID, new_task)

    def test_update_schedule_task_by_user__should_update_existing_record(self):
        new_task_type = 'turn on'
        new_task = {'taskId': self.TASK_ID, 'alarmDays': 'SatSun', 'alarmGroupName': 'private potty room', 'taskType': new_task_type, 'enabled':  False}
        with UserDatabaseManager() as database:
            task_type = database.session.query(ScheduledTaskTypes).filter_by(activity_name='turn off').first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with UserDatabaseManager() as database:
            database.update_schedule_task_by_user_id(self.USER_ID, new_task)

        with UserDatabaseManager() as database:
            actual = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert actual.alarm_days == 'SatSun'
            assert actual.alarm_group_name == 'private potty room'
            assert actual.id != self.TASK_ID
            assert actual.task_type.activity_name == new_task_type
            assert actual.enabled is False

    def test_delete_schedule_tasks_by_user__should_not_throw_when_record_does_not_exist(self):
        with UserDatabaseManager() as database:
            database.delete_schedule_task_by_user(self.USER_ID, self.TASK_ID)

        with UserDatabaseManager() as database:
            actual = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert actual is None

    def test_get_preferences_by_user__should_return_preferences_for_valid_user(self):
        with UserDatabaseManager() as database:
            response = database.get_preferences_by_user(self.USER_ID)

            assert response['temp_unit'] == 'fahrenheit'
            assert response['measure_unit'] == 'imperial'
            assert response['city'] == self.CITY
            assert response['is_fahrenheit'] is True
            assert response['is_imperial'] is True
            assert response['garage_door'] == self.GARAGE
            assert response['garage_id'] == 1

    def test_get_preferences_by_user__should_raise_bad_request_when_no_preferences(self):
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                bad_user_id = str(uuid.uuid4())
                database.get_preferences_by_user(bad_user_id)

    def test_insert_preferences_by_user__should_insert_valid_preferences(self):
        city = 'Vienna'
        new_door = 'Kalynns'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False, 'garageDoor': new_door, 'garageId': 5}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            database.session.commit()
            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.garage_door == new_door
            assert actual.garage_id == 5

    def test_insert_preferences_by_user__should_not_fail_when_time_is_none(self):
        city = 'Vienna'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False, 'garageDoor': 3}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True

    def test_insert_preferences_by_user__should_not_nullify_city_when_missing(self):
        preference_info = {'isFahrenheit': False, 'isImperial': True, 'garagaeDoor': 2}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == self.CITY
            assert actual.is_fahrenheit is False
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_is_fahrenheit_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isImperial': False, 'garageDoor': 1}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is False

    def test_insert_preferences_by_user__should_not_nullify_is_imperial_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'garageDoor': 1}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_garage_door_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE

    def test_insert_preferences_by_user__should_not_nullify_garage_id_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE
            assert actual.garage_id == 1

    def test_insert_preferences_by_user__should_set_garage_id_to_null_when_sent_null(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True, 'garageId': None}
        with UserDatabaseManager() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE
            assert actual.garage_id is None


class TestDbSumpIntegration:
    DEPTH = 8.0
    FIRST_USER_ID = str(uuid.uuid4())
    SECOND_USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    DAY = datetime.datetime.date(datetime.datetime.now())
    DATE = datetime.datetime.now()

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.FIRST_USER = UserInformation(id=self.FIRST_USER_ID, first_name='Jon', last_name='Test')
        self.SECOND_USER = UserInformation(id=self.SECOND_USER_ID, first_name='Dylan', last_name='Fake')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.FIRST_SUMP_DAILY = DailySumpPumpLevel(id=88, distance=11.0, user_id=self.FIRST_USER_ID, warning_level=2, create_date=self.DATE)
        self.SECOND_SUMP_DAILY = DailySumpPumpLevel(id=99, distance=self.DEPTH, user_id=self.SECOND_USER_ID, warning_level=1, create_date=self.DATE)
        self.THIRD_SUMP_DAILY = DailySumpPumpLevel(id=100, distance=12.0, user_id=self.SECOND_USER_ID, warning_level=2, create_date=self.DATE)
        self.FIRST_SUMP_AVG = AverageSumpPumpLevel(id=34, user_id=self.FIRST_USER_ID, distance=12.0, create_day=self.DAY)
        self.SECOND_SUMP_AVG = AverageSumpPumpLevel(id=35, user_id=self.FIRST_USER_ID, distance=self.DEPTH, create_day=self.DAY)
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.FIRST_USER_ID, child_user_id=self.CHILD_USER_ID)

        with UserDatabaseManager() as database:
            database.session.add_all([self.FIRST_USER, self.SECOND_USER, self.CHILD_USER])
            database.session.add_all([self.FIRST_SUMP_AVG, self.SECOND_SUMP_AVG])
            database.session.add_all([self.FIRST_SUMP_DAILY, self.SECOND_SUMP_DAILY, self.THIRD_SUMP_DAILY])
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.FIRST_SUMP_DAILY)
            database.session.delete(self.SECOND_SUMP_DAILY)
            database.session.delete(self.THIRD_SUMP_DAILY)
            database.session.delete(self.FIRST_SUMP_AVG)
            database.session.delete(self.SECOND_SUMP_AVG)
            database.session.delete(self.CHILD_ACCOUNT)
            database.session.delete(self.SECOND_USER)
            database.session.delete(self.FIRST_USER)
            database.session.delete(self.CHILD_USER)
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

    def test_get_current_sump_level_by_user__should_return_parent_records_for_child(self):
        with UserDatabaseManager() as database:
            actual = database.get_current_sump_level_by_user(self.CHILD_USER_ID)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_raise_bad_request_when_user_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_current_sump_level_by_user(str(uuid.uuid4()))

    def test_get_average_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with UserDatabaseManager() as database:
            actual = database.get_average_sump_level_by_user(self.FIRST_USER_ID)
            assert actual == {'averageDepth': self.DEPTH, 'latestDate': str(self.DAY)}

    def test_get_average_sump_level_by_user__should_return_parent_records_for_child(self):
        with UserDatabaseManager() as database:
            actual = database.get_average_sump_level_by_user(self.CHILD_USER_ID)
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


class TestDbPasswordIntegration:
    USER_NAME = 'JonsUser'
    PASSWORD = 'BESTESTPASSWORDEVA'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.USER_INFO = UserInformation(first_name='test', last_name='Tester', id=self.USER_ID)
        self.USER_CREDS = UserCredentials(id=str(uuid.uuid4()), user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_CREDS)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_CREDS)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_change_user_password__should_raise_exception_with_mismatched_password(self):
        mismatched_pass = 'this wont match'
        new_pass = 'doesnt matter'
        with pytest.raises(Unauthorized):
            with UserDatabaseManager() as database:
                database.change_user_password(self.USER_ID, mismatched_pass, new_pass)

    def test_change_user_password__should_change_user_password_when_matching(self):
        new_pass = 'I SHOULD HAVE CHANGED!!!'
        with UserDatabaseManager() as database:
            database.change_user_password(self.USER_ID, self.PASSWORD, new_pass)

            user = database.session.query(UserCredentials).filter_by(user_name=self.USER_NAME).first()
            assert user.password == new_pass


class TestDbRoleIntegration:
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    ROLE_NAME = "lighting"

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='steve', last_name='rogers')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="lighting", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID, role=self.ROLE)
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=False)
        with UserDatabaseManager() as database:
            database.session.add(self.ROLE)
            database.session.add_all([self.USER_INFO, self.CHILD_USER])
            database.session.add(self.USER_ROLE)
            database.session.add(self.USER_PREF)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.delete(self.USER_PREF)
            database.session.delete(self.CHILD_ACCOUNT)
            database.session.delete(self.USER_ROLE)
            database.session.commit()
            database.session.delete(self.USER_INFO)
            database.session.delete(self.CHILD_USER)
            database.session.delete(self.ROLE)
            database.session.query(RoleDeviceNodes).delete()
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_add_new_device__should_raise_unauthorized_when_no_role_found(self):
        role_name = 'garage_door'
        ip_address = '0.0.0.0'
        with pytest.raises(Unauthorized):
            with UserDatabaseManager() as database:
                database.add_new_role_device(self.USER_ID, role_name, ip_address)

    def test_add_new_device__should_insert_a_new_device_into_table(self):
        ip_address = '192.168.1.145'
        with UserDatabaseManager() as database:
            database.add_new_role_device(self.USER_ID, self.ROLE_NAME, ip_address)

            actual = database.session.query(RoleDevices).filter_by(user_role_id=self.USER_ROLE_ID).first()
            assert actual.ip_address == ip_address

    def test_add_new_device__should_register_new_device_to_parent_from_child(self):
        ip_address = '192.168.1.145'
        with UserDatabaseManager() as database:
            device_id = database.add_new_role_device(self.CHILD_USER_ID, self.ROLE_NAME, ip_address)

            actual = database.session.query(RoleDevices).filter_by(id=device_id).first()

            assert actual.ip_address == ip_address

    def test_add_new_device_node__should_raise_unauthorized_when_no_device_found(self):
        ip_address = '1.1.1.1'
        device_id = str(uuid.uuid4())
        node_name = 'test node'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            with pytest.raises(Unauthorized):
                database.add_new_device_node(self.USER_ID, str(uuid.uuid4()), node_name, False)

    def test_add_new_device_node__should_insert_a_new_node_into_table(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actual = database.session.query(RoleDeviceNodes).filter_by(role_device_id=device_id).first()
            assert actual.node_name == node_name
            database.session.delete(actual)

    def test_add_new_device_node__should_return_available_nodes_left(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            actual = database.add_new_device_node(self.USER_ID, device_id, node_name, False)
            assert actual['availableNodes'] == 1

    def test_add_new_device_node__should_set_node_device_to_one_when_first_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actual = database.session.query(RoleDeviceNodes).filter_by(role_device_id=device_id).first()
            assert actual.node_device == 1

    def test_add_new_device_node__should_set_node_device_to_two_when_second_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'second garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            node = RoleDeviceNodes(node_name='test', node_device=1, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actuals = database.session.query(RoleDeviceNodes).filter_by(role_device_id=device_id).all()
            assert len(actuals) == 2
            assert [actual.node_device for actual in actuals] == [1,2]

    def test_add_new_device_node__should_set_node_device_to_three_when_third_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'third garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=3, ip_address=ip_address)
            node_one = RoleDeviceNodes(node_name='test 1', node_device=1, role_device_id=device_id)
            node_two = RoleDeviceNodes(node_name='test 2', node_device=2, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node_one)
            database.session.add(node_two)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actuals = database.session.query(RoleDeviceNodes).filter_by(role_device_id=device_id).all()
            assert len(actuals) == 3
            assert [actual.node_device for actual in actuals] == [1,2,3]

    def test_add_new_device_node__should_raise_bad_request_when_exceeding_max_nodes(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'third garage door'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            node_one = RoleDeviceNodes(node_name='test 1', node_device=1, role_device_id=device_id)
            node_two = RoleDeviceNodes(node_name='test 2', node_device=2, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node_one)
            database.session.add(node_two)

            with pytest.raises(BadRequest):
                database.add_new_device_node(self.USER_ID, device_id, node_name, False)

    def test_add_new_device_node__should_update_preference_when_flag_set_to_true(self):
        device_id = str(uuid.uuid4())
        node_name = 'Jons New'
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address='1.1.1.1')
            database.session.add(device)
            database.add_new_device_node(self.USER_ID, device_id, node_name, True)

        with UserDatabaseManager() as database:
            actual = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()
            assert actual.garage_door == node_name
            assert actual.garage_id == 1

    def test_get_user_garage_ip__should_return_garage_ip(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        with UserDatabaseManager() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            actual = database.get_user_garage_ip(self.USER_ID)

            assert actual == ip_address

    def test_get_user_garage_ip__should_raise_bad_request_when_not_found(self):
        with UserDatabaseManager() as database:
            with pytest.raises(BadRequest):
                database.get_user_garage_ip(str(uuid.uuid4()))


@patch('svc.db.methods.user_credentials.uuid')
class TestUserDuplication:
    PASSWORD = "Test"
    USER_NAME = "tony_stank  "
    ROLE_NAME = "lighting"
    CITY = 'Des Moines'
    GROUP_NAME = 'Bed Room'
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    CRED_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    UPDATED_USER_ID = uuid.uuid4()
    USER_ROLE_ID = str(uuid.uuid4())
    UPDATED_DEVICE_ID = str(uuid.uuid4())

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="lighting", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID, role=self.ROLE)
        self.ROLE_DEVICE = RoleDevices(user_role_id=self.USER_ROLE_ID, ip_address='0.0.0.0', max_nodes=1)
        self.USER_LOGIN = UserCredentials(id=self.CRED_ID, user_name=self.USER_NAME, password=self.PASSWORD, user_id=self.USER_ID)
        self.CHILD_USER = UserCredentials(id=str(uuid.uuid4()), user_name='Steve Rogers', password='', user_id=self.CHILD_USER_ID)
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)

        with UserDatabaseManager() as database:
            database.session.add(self.ROLE)
            database.session.add(self.USER_INFO)
            database.session.add(self.USER_LOGIN)
            database.session.add(self.USER_ROLE)
            database.session.add(self.ROLE_DEVICE)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(RoleDevices).filter_by(user_role_id=self.USER_ROLE_ID).delete()
            database.session.query(RoleDevices).filter_by(id=self.UPDATED_DEVICE_ID).delete()
            database.session.query(UserPreference).filter_by(user_id=str(self.USER_ID)).delete()
            database.session.query(UserPreference).filter_by(user_id=str(self.UPDATED_USER_ID)).delete()
            database.session.query(UserRoles).filter_by(user_id=str(self.UPDATED_USER_ID)).delete()
            database.session.query(UserRoles).filter_by(user_id=self.USER_ID).delete()
            database.session.commit()
            database.session.query(ChildAccounts).delete()
            database.session.query(UserCredentials).filter_by(user_id=self.USER_ID).delete()
            database.session.query(UserCredentials).filter_by(user_id=self.CHILD_USER_ID).delete()
            database.session.query(UserCredentials).filter_by(user_id=str(self.UPDATED_USER_ID)).delete()
            database.session.query(UserInformation).filter_by(id=str(self.UPDATED_USER_ID)).delete()
            database.session.query(UserInformation).filter_by(id=self.USER_ID).delete()
            database.session.query(UserInformation).filter_by(id=self.CHILD_USER_ID).delete()
            database.session.query(Roles).filter_by(id=self.ROLE_ID).delete()
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_create_child_account__should_duplicate_existing_record(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4()]
        new_email = 'tony_stank@stark.com'

        with UserDatabaseManager() as database:
            database.create_child_account(self.USER_ID, new_email, [], self.PASSWORD)

            actual = database.session.query(UserInformation).filter_by(id=str(self.UPDATED_USER_ID)).first()
            assert actual.email == new_email
            assert actual.id == str(self.UPDATED_USER_ID)

    def test_create_child_account__should_duplicate_existing_records_devices(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'

        with UserDatabaseManager() as database:
            database.create_child_account(self.USER_ID, new_email, [self.ROLE_NAME], self.PASSWORD)
            database.session.commit()

            actual = database.session.query(UserRoles).filter_by(user_id=str(self.UPDATED_USER_ID)).all()
            lighting_role = next(x for x in actual if x.role.role_name == self.ROLE_NAME)
            assert lighting_role.role_devices.ip_address == '0.0.0.0'

    def test_create_child_account__should_not_duplicate_existing_records_devices_when_none_present(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'

        with UserDatabaseManager() as database:
            database.session.query(RoleDevices).filter_by(user_role_id=self.USER_ROLE_ID).delete()

        with UserDatabaseManager() as database:
            database.create_child_account(self.USER_ID, new_email, [self.ROLE_NAME], self.PASSWORD)
            database.session.commit()

            actual = database.session.query(UserRoles).filter_by(user_id=str(self.UPDATED_USER_ID)).all()
            lighting_role = next(x for x in actual if x.role.role_name == self.ROLE_NAME)
            assert lighting_role.role_devices is None

    def test_create_child_account__should_reduce_roles(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        new_email = 'tony_stank@stark.com'
        role_name = "security"
        role = Roles(id=str(uuid.uuid4()), role_desc=role_name, role_name=role_name)
        second_role = UserRoles(id=str(uuid.uuid4()), user_id=self.USER_ID, role_id=self.ROLE_ID, role=role)
        with UserDatabaseManager() as database:
            database.session.add(second_role)
            database.session.commit()
            database.create_child_account(self.USER_ID, new_email, [role_name], self.PASSWORD)

            actual = database.session.query(UserRoles).filter_by(user_id=str(self.UPDATED_USER_ID)).all()
            assert len(actual) == 1
            assert actual[0].role.role_name == role_name

    def test_create_child_account__should_throw_bad_request_when_no_user_exists(self, mock_uuid):
        with pytest.raises(BadRequest):
            with UserDatabaseManager() as database:
                database.create_child_account(str(uuid.uuid4()), "", [], self.PASSWORD)

    def test_create_child_account__should_throw_bad_request_when_child_account(self, mock_uuid):
        with pytest.raises(BadRequest):
            user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
            with UserDatabaseManager() as database:
                database.session.add(user)
                database.session.add(self.CHILD_USER)
                database.session.commit()
                database.session.add(self.CHILD_ACCOUNT)
                database.create_child_account(self.CHILD_USER_ID, "test@test.com", ['lighting'], self.PASSWORD)

    def test_create_child_account__should_create_preferences(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4(), self.UPDATED_DEVICE_ID]
        with UserDatabaseManager() as database:
            database.create_child_account(self.USER_ID, self.USER_NAME, [self.ROLE_NAME], self.PASSWORD)

        with UserDatabaseManager() as database:
            new_user = database.session.query(UserPreference).filter_by(user_id=str(self.UPDATED_USER_ID)).first()
            assert new_user.city == self.CITY
            assert new_user.is_fahrenheit is True
            assert new_user.is_imperial is True

    def test_create_child_account__should_create_child_account_record(self, mock_uuid):
        mock_uuid.uuid4.side_effect = [self.UPDATED_USER_ID, uuid.uuid4(), uuid.uuid4()]
        new_email = 'tony_stank@stark.com'

        with UserDatabaseManager() as database:
            actual = database.create_child_account(self.USER_ID, new_email, [], self.PASSWORD)

            assert actual[0].get('user_name') == new_email
            assert actual[0].get('user_id') == str(self.UPDATED_USER_ID)
            assert actual[0].get('roles') == []

    def test_get_user_child_accounts__should_return_children_accounts(self, mock_uuid):
        user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with UserDatabaseManager() as database:
            database.session.add(user)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

            actual = database.get_user_child_accounts(self.USER_ID)

            assert actual == [{'user_name': 'Steve Rogers', 'user_id': self.CHILD_USER_ID, 'roles': []}]

    def test_delete_child_user_account__should_remove_existing_child_account(self, mock_uuid):
        user = UserInformation(id=self.CHILD_USER_ID, first_name='Steve', last_name='Rogers')
        with UserDatabaseManager() as database:
            database.session.add(user)
            database.session.add(self.CHILD_USER)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

        with UserDatabaseManager() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with UserDatabaseManager() as database:
            actual_child_account = database.session.query(ChildAccounts).filter_by(child_user_id=self.CHILD_USER_ID).first()
            assert actual_child_account is None
            actual_child_user = database.session.query(UserCredentials).filter_by(user_id=self.CHILD_USER_ID).first()
            assert actual_child_user is None

    def test_delete_child_user_account__should_not_delete_parent_when_no_child(self, mock_uuid):
        with UserDatabaseManager() as database:
            database.delete_child_user_account(self.USER_ID, self.CHILD_USER_ID)

        with UserDatabaseManager() as database:
            actual_child_account = database.session.query(ChildAccounts).filter_by(child_user_id=self.CHILD_USER_ID).first()
            assert actual_child_account is None
            actual_child_user = database.session.query(UserCredentials).filter_by(user_id=self.CHILD_USER_ID).first()
            assert actual_child_user is None
            actual_parent = database.session.query(UserCredentials).filter_by(user_id=self.USER_ID).first()
            assert actual_parent is not None


class TestUserScenes:
    SCENE_ID = str(uuid.uuid4())
    USER_ID = str(uuid.uuid4())
    SCENE_NAME = 'Movie'
    GROUP_NAME = 'living room'

    def setup_method(self):
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.SCENE = Scenes(name=self.SCENE_NAME, user_id=self.USER_ID, id=self.SCENE_ID)
        self.DETAIL = SceneDetails(light_group='2', light_group_name=self.GROUP_NAME, light_brightness=45, scene_id=self.SCENE_ID)
        os.environ.update({'SQL_USERNAME': DB_USER, 'SQL_PASSWORD': DB_PASS,
                           'SQL_DBNAME': DB_NAME, 'SQL_PORT': DB_PORT})
        with UserDatabaseManager() as database:
            database.session.add(self.USER_INFO)
            database.session.commit()
            database.session.add(self.SCENE)
            database.session.add(self.DETAIL)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(SceneDetails).delete()
            database.session.commit()
            database.session.query(Scenes).delete()
            database.session.delete(self.USER_INFO)
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_scenes_by_user__should_return_records(self):
        with UserDatabaseManager() as database:
            actual = database.get_scenes_by_user(self.USER_ID)

        assert actual[0]['name'] == self.SCENE_NAME
        assert actual[0]['lights'][0]['group_name'] == self.GROUP_NAME

    def test_get_scenes_by_user__should_return_empty_list_when_none(self):
        with UserDatabaseManager() as database:
            actual = database.get_scenes_by_user(str(uuid.uuid4()))

        assert actual == []

    def test_delete_scene_by_user__should_delete_record(self):
        with UserDatabaseManager() as database:
            database.delete_scene_by_user(self.USER_ID, self.SCENE_ID)

        with UserDatabaseManager() as database:
            actual = database.session.query(Scenes).filter_by(user_id=self.USER_ID).all()
            assert len(actual) == 0
