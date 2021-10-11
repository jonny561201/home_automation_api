import json
import os
import uuid
from datetime import datetime, timedelta

import jwt
import pytz

from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, UserPreference, ScheduleTasks, ScheduledTaskTypes, \
    RefreshToken, UserCredentials
from svc.manager import app


class TestAppRoutesIntegration:
    db_user = 'postgres'
    db_pass = 'password'
    db_port = '5432'
    db_name = 'garage_door'
    JWT_SECRET = 'testSecret'
    USER_ID = str(uuid.uuid4())
    CITY = 'Prague'

    def setup_method(self):
        Settings.get_instance().dev_mode = False
        os.environ.update({'SQL_USERNAME': self.db_user, 'SQL_PASSWORD': self.db_pass, 'JWT_SECRET': self.JWT_SECRET,
                           'SQL_DBNAME': self.db_name, 'SQL_PORT': self.db_port})
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, city=self.CITY, is_fahrenheit=True, is_imperial=True)

        with UserDatabaseManager() as database:
            database.session.add(self.USER)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(ScheduleTasks).delete()
            database.session.delete(self.PREFERENCE)
            database.session.delete(self.USER)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_health_check__should_return_success(self):
        actual = self.TEST_CLIENT.get('healthCheck')

        assert actual.status_code == 200
        assert actual.data.decode('UTF-8') == 'Success'

    def test_login__should_return_401_when_invalid_user(self):
        user_name = 'not_real_user'
        user_pass = 'wrongPass'
        request = {'grant_type': 'client_credentials', 'client_id': user_name, 'client_secret': user_pass}

        actual = self.TEST_CLIENT.post('token', data=json.dumps(request))

        assert actual.status_code == 401

    def test_login__should_return_401_when_invalid_password(self):
        user_name = 'not_real_user'
        user_pass = 'wrongPass'
        request = {'grant_type': 'client_credentials', 'client_id': user_name, 'client_secret': user_pass}

        actual = self.TEST_CLIENT.post('token', data=json.dumps(request))

        assert actual.status_code == 401

    def test_login__should_return_success_when_user_valid(self):
        user_name = 'Jonny561201'
        user_pass = 'password'
        request = {'grant_type': 'client_credentials', 'client_id': user_name, 'client_secret': user_pass}

        actual = self.TEST_CLIENT.post('token', data=json.dumps(request))

        assert actual.status_code == 200

    def test_get_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/preferences', headers=headers)

        assert actual.status_code == 401

    def test_get_user_preferences_by_user_id__should_return_success_when_valid_user(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/preferences', headers=headers)

        assert actual.status_code == 200
        assert json.loads(actual.data).get('city') == self.CITY

    def test_update_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/preferences/update', headers=headers)

        assert actual.status_code == 401

    def test_update_user_preferences_by_user_id__should_successfully_update_user(self):
        expected_city = 'Shannon'
        post_body = json.dumps({'city': expected_city, 'isFahrenheit': False})
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/preferences/update', data=post_body, headers=headers)

        assert actual.status_code == 200
        with UserDatabaseManager() as database:
            preference = database.session.query(UserPreference).filter_by(user_id=self.USER_ID).first()
            assert preference.city == expected_city

    # def test_get_user_tasks_by_user_id__should_return_401_when_unauthorized(self):
    #     bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
    #     headers = {'Authorization': bearer_token}
    #
    #     actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/tasks', headers=headers)
    #
    #     assert actual.status_code == 401

    def test_get_user_tasks_by_user_id__should_successfully_retrieve_user(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/tasks', headers=headers)

        assert actual.status_code == 200

    def test_get_user_tasks_by_user_id__should_successfully_retrieve_user_by_type(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/tasks/hvac', headers=headers)

        assert actual.status_code == 200

    def test_delete_user_tasks_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        task_id = str(uuid.uuid4())
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.delete(f'userId/{self.USER_ID}/tasks/{task_id}', headers=headers)

        assert actual.status_code == 401

    def test_delete_user_tasks_by_user_id__should_successfully_update_user(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        task_id = str(uuid.uuid4())
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.delete(f'userId/{self.USER_ID}/tasks/{task_id}', headers=headers)

        assert actual.status_code == 200

    def test_insert_user_task_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        request_data = json.dumps({'alarm_time': '00:00:01'})
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/tasks', data=request_data, headers=headers)

        assert actual.status_code == 401

    def test_insert_user_task_by_user_id__should_successfully_update_user(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        request_data = json.dumps({'alarmTime': '00:00:01', 'alarmGroupName': 'potty room', 'alarmLightGroup': '43', 'alarmDays': 'Wed',
                                   'taskType': 'turn on', 'enabled': True, 'hvacMode': 'HEAT', 'hvacStart': '01:01:01', 'hvacStop': '02:02:02'})
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/tasks', data=request_data, headers=headers)

        assert actual.status_code == 200

    def test_update_user_task_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        request_data = json.dumps({'alarm_time': '00:00:01'})
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/tasks/update', data=request_data, headers=headers)

        assert actual.status_code == 401

    def test_update_user_task_by_user_id__should_successfully_update_user(self):
        task_id = str(uuid.uuid4())
        task = ScheduleTasks(user_id=self.USER_ID, id=task_id, alarm_group_name='fake room', alarm_light_group='42', alarm_days='Mon', enabled=False, hvac_mode='HEAT')
        with UserDatabaseManager() as database:
            task_type = database.session.query(ScheduledTaskTypes).first()
            task.task_type = task_type
            database.session.add(task)

        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        new_day = 'Wed'
        new_room = 'potty room'
        request_data = json.dumps({'taskId': task_id, 'alarmTime': '00:00:01', 'alarmGroupName': new_room, 'alarmLightGroup': '43',
                                   'alarmDays': new_day, 'taskType': 'turn off', 'enabled': False, 'hvacMode': 'COOL'})
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.post(f'userId/{self.USER_ID}/tasks/update', data=request_data, headers=headers)
        assert actual.status_code == 200

        with UserDatabaseManager() as database:
            record = database.session.query(ScheduleTasks).filter_by(user_id=self.USER_ID).first()
            assert record.alarm_group_name == new_room
            assert record.alarm_days == new_day
            assert record.hvac_mode == 'COOL'


class TestRefreshTokenApp:
    db_user = 'postgres'
    db_pass = 'password'
    db_port = '5432'
    db_name = 'garage_door'
    JWT_SECRET = 'testSecret'
    USER_ID = str(uuid.uuid4())
    BAD_TOKEN = str(uuid.uuid4())
    GOOD_TOKEN = str(uuid.uuid4())
    FUTURE_TIME = datetime.now(tz=pytz.timezone('US/Central')) + timedelta(hours=12)
    EXPIRED_TIME = datetime.now(tz=pytz.timezone('US/Central')) - timedelta(hours=1)

    def setup_method(self):
        Settings.get_instance().dev_mode = False
        os.environ.update({'SQL_USERNAME': self.db_user, 'SQL_PASSWORD': self.db_pass, 'JWT_SECRET': self.JWT_SECRET,
                           'SQL_DBNAME': self.db_name, 'SQL_PORT': self.db_port})
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.GOOD_REFRESH = RefreshToken(id=str(uuid.uuid4()), user_id=self.USER_ID, refresh=self.GOOD_TOKEN, count=1, expire_time=self.FUTURE_TIME)
        self.BAD_REFRESH = RefreshToken(id=str(uuid.uuid4()), user_id=self.USER_ID, refresh=self.BAD_TOKEN, count=1, expire_time=self.EXPIRED_TIME)
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.USER_CREDS = UserCredentials(id=str(uuid.uuid4()), user_name="test", password="test", user=self.USER, user_id=self.USER_ID)

        with UserDatabaseManager() as database:
            database.session.add(self.USER)
        with UserDatabaseManager() as database:
            database.session.add(self.USER_CREDS)
            database.session.add(self.BAD_REFRESH)
            database.session.add(self.GOOD_REFRESH)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(RefreshToken).delete()
            database.session.query(ScheduleTasks).delete()
            database.session.delete(self.USER_CREDS)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_refreshed_bearer_token__should_return_forbidden_when_token_count_expired(self):
        request_data = {'refresh_token': self.BAD_TOKEN, 'grant_type': 'refresh_token'}
        actual = self.TEST_CLIENT.post(f'token', data=json.dumps(request_data))

        assert actual.status_code == 403
