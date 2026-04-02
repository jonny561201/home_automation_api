import json
import uuid

import jwt
from sqlalchemy import delete, select

from integration.route_base import mock_jwks_token
from svc.db.models.user_information_model import UserInformation, UserPreference, ScheduleTasks, ScheduledTaskTypes
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestAppRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    CITY = 'Prague'
    CONTENT_HEADER = {'Content-Type': 'application/json'}

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADERS = {'Authorization': f'Bearer {self.TOKEN}', 'Content-Type': 'application/json'}

        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.PREFERENCE = UserPreference(user_id=self.USER_ID, city=self.CITY, is_fahrenheit=True, is_imperial=True)

        with DatabaseBase() as database:
            database.session.add(self.USER)
            database.session.add(self.PREFERENCE)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_health_check__should_return_success(self):
        actual = self.TEST_CLIENT.get('healthCheck')

        assert actual.status_code == 200
        assert actual.data.decode('UTF-8') == 'Success'

    def test_get_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.get(f'preferences', headers=headers)

        assert actual.status_code == 401

    def test_get_user_preferences_by_user_id__should_return_success_when_valid_user(self):
        actual = self.TEST_CLIENT.get(f'preferences', headers=self.HEADERS)

        assert actual.status_code == 200
        assert json.loads(actual.data).get('city') == self.CITY

    def test_update_user_preferences_by_user_id__should_return_401_when_unauthorized(self):
        actual = self.TEST_CLIENT.post(f'preferences/update', data='{}', headers=self.CONTENT_HEADER)

        assert actual.status_code == 401

    def test_update_user_preferences_by_user_id__should_successfully_update_user(self):
        expected_city = 'Shannon'
        post_body = json.dumps({'city': expected_city, 'isFahrenheit': False})

        actual = self.TEST_CLIENT.post(f'preferences/update', data=post_body, headers=self.HEADERS)

        assert actual.status_code == 200
        with DatabaseBase() as database:
            preference = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()
            assert preference.city == expected_city

    # def test_get_user_tasks_by_user_id__should_return_401_when_unauthorized(self):
    #     bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
    #     headers = {'Authorization': bearer_token}
    #
    #     actual = self.TEST_CLIENT.get(f'userId/{self.USER_ID}/tasks', headers=headers)
    #
    #     assert actual.status_code == 401

    def test_get_user_tasks_by_user_id__should_successfully_retrieve_user(self):
        actual = self.TEST_CLIENT.get(f'tasks', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_get_user_tasks_by_user_id__should_successfully_retrieve_user_by_type(self):
        actual = self.TEST_CLIENT.get(f'tasks/hvac', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_delete_user_tasks_by_user_id__should_return_401_when_unauthorized(self):
        bearer_token = jwt.encode({}, 'bad secret', algorithm='HS256')
        task_id = str(uuid.uuid4())
        headers = {'Authorization': bearer_token}

        actual = self.TEST_CLIENT.delete(f'tasks/{task_id}', headers=headers)

        assert actual.status_code == 401

    def test_delete_user_tasks_by_user_id__should_successfully_update_user(self):
        task_id = str(uuid.uuid4())

        actual = self.TEST_CLIENT.delete(f'tasks/{task_id}', headers=self.HEADERS)

        assert actual.status_code == 200

    def test_insert_user_task_by_user_id__should_return_401_when_unauthorized(self):
        request_data = json.dumps({'alarm_time': '00:00:01'})

        actual = self.TEST_CLIENT.post(f'tasks', data=request_data, headers=self.CONTENT_HEADER)

        assert actual.status_code == 401

    def test_insert_user_task_by_user_id__should_successfully_update_user(self):
        request_data = json.dumps({'alarmTime': '00:00:01', 'alarmGroupName': 'potty room', 'alarmLightGroup': '43', 'alarmDays': 'Wed',
                                   'taskType': 'turn on', 'enabled': True, 'hvacMode': 'HEAT', 'hvacStart': '01:01:01', 'hvacStop': '02:02:02'})

        actual = self.TEST_CLIENT.post(f'tasks', data=request_data, headers=self.HEADERS)

        assert actual.status_code == 200

    def test_update_user_task_by_user_id__should_return_401_when_unauthorized(self):
        request_data = json.dumps({'alarm_time': '00:00:01'})

        actual = self.TEST_CLIENT.post(f'tasks/update', data=request_data, headers=self.CONTENT_HEADER)

        assert actual.status_code == 401

    def test_update_user_task_by_user_id__should_successfully_update_user(self):
        task_id = str(uuid.uuid4())
        task = ScheduleTasks(user_id=self.USER_ID, id=task_id, alarm_group_name='fake room', alarm_light_group='42', alarm_days='Mon', enabled=False, hvac_mode='HEAT')
        with DatabaseBase() as database:
            task_type = database.session.execute(select(ScheduledTaskTypes)).scalars().first()
            task.task_type = task_type
            database.session.add(task)

        new_day = 'Wed'
        new_room = 'potty room'
        request_data = json.dumps({'taskId': task_id, 'alarmTime': '00:00:01', 'alarmGroupName': new_room, 'alarmLightGroup': '43',
                                   'alarmDays': new_day, 'taskType': 'turn off', 'enabled': False, 'hvacMode': 'COOL'})

        actual = self.TEST_CLIENT.post(f'tasks/update', data=request_data, headers=self.HEADERS)
        assert actual.status_code == 200

        with DatabaseBase() as database:
            record = database.session.execute(select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)).scalars().first()
            assert record.alarm_group_name == new_room
            assert record.alarm_days == new_day
            assert record.hvac_mode == 'COOL'
