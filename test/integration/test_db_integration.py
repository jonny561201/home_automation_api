import datetime
import uuid
from zoneinfo import ZoneInfo

import pytest
from mock import patch
from sqlalchemy import delete, select
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden

from svc.db.repositories.account_repository import AccountRepository
from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.lights_repository import LightsRepository
from svc.db.repositories.tasks_repository import TasksRepository
from svc.db.repositories.credential_repository import CredentialRepository
from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import UserInformation, UserCredentials, Roles, UserPreference, UserRoles, \
    RoleDevices, RoleDeviceNodes, ChildAccounts, ScheduleTasks, \
    ScheduledTaskTypes, Scenes, SceneDetails, RefreshToken
from svc.models.app import Tasks
from svc.models.scenes import LightScenes


class TestDbTaskIntegration:
    USER_ID = str(uuid.uuid4())
    TASK_ID = str(uuid.uuid4())
    CITY = 'Praha'
    LIGHT_GROUP = '42'
    LIGHT_TIME = '02:22:22'
    GROUP_NAME = 'secret room'
    DAYS = 'MonTueWedThuFri'
    GARAGE = 'Jons'

    def setup_method(self):

        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.TASK = ScheduleTasks(user_id=self.USER_ID, id=self.TASK_ID, alarm_light_group=self.LIGHT_GROUP, alarm_group_name=self.GROUP_NAME, alarm_days=self.DAYS, alarm_time=datetime.time.fromisoformat(self.LIGHT_TIME), enabled=True)
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY, garage_door=self.GARAGE, garage_id=1)
        with DatabaseBase() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(ScheduleTasks))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_schedule_task_by_user__should_return_task(self):
        with TasksRepository() as database:
            task_type = database.session.execute(select(ScheduledTaskTypes)).scalars().first()
            task_name = task_type.activity_name
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with TasksRepository() as database:
            actual = database.get_schedule_tasks_by_user(self.USER_ID, None)
            assert actual.tasks[0].alarmLightGroup == self.LIGHT_GROUP
            assert actual.tasks[0].alarmGroupName == self.GROUP_NAME
            assert actual.tasks[0].alarmDays == self.DAYS
            assert actual.tasks[0].alarmTime == self.LIGHT_TIME
            assert actual.tasks[0].taskId == self.TASK_ID
            assert actual.tasks[0].enabled == True
            assert actual.tasks[0].taskType == task_name

    def test_get_schedule_task_by_user__should_return_empty_list_when_no_matches(self):
        user_id = str(uuid.uuid4())
        with TasksRepository() as database:
            actual = database.get_schedule_tasks_by_user(user_id, None)
            assert actual == Tasks([])

    def test_insert_schedule_task_by_user__should_insert_task(self):
        task = {'alarmTime': self.LIGHT_TIME, 'alarmLightGroup': self.LIGHT_GROUP, 'alarmGroupName': self.GROUP_NAME, 'alarmDays': self.DAYS, 'enabled': False, 'taskType': 'turn on'}
        with TasksRepository() as database:
            database.insert_schedule_task_by_user(self.USER_ID, task)

        with TasksRepository() as database:
            stmt = select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)
            actual = database.session.execute(stmt).scalars().first()
            assert str(actual.user_id) == self.USER_ID
            assert actual.alarm_light_group == self.LIGHT_GROUP
            assert actual.alarm_time == datetime.time.fromisoformat(self.LIGHT_TIME)
            assert actual.alarm_days == self.DAYS
            assert actual.alarm_group_name == self.GROUP_NAME
            assert actual.enabled is False

    def test_insert_schedule_task_by_user__should_insert_task_for_all_rooms(self):
        task = {'alarmTime': self.LIGHT_TIME, 'alarmLightGroup': '0', 'alarmGroupName': self.GROUP_NAME, 'alarmDays': self.DAYS, 'enabled': False, 'taskType': 'turn on'}
        with TasksRepository() as database:
            database.insert_schedule_task_by_user(self.USER_ID, task)

        with TasksRepository() as database:
            actual = database.session.execute(select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)).scalars().first()
            assert str(actual.user_id) == self.USER_ID
            assert actual.alarm_light_group == '0'

    def test_delete_schedule_tasks_by_user__should_delete_record_that_already_exists(self):
        with TasksRepository() as database:
            task_type = database.session.execute(select(ScheduledTaskTypes)).scalars().first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with TasksRepository() as database:
            database.delete_schedule_task_by_user(self.USER_ID, self.TASK_ID)

        with TasksRepository() as database:
            actual = database.session.execute(select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)).first()
            assert actual is None

    def test_update_schedule_task_by_user__should_raise_bad_request_when_user_does_not_exist(self):
        new_task = {'taskId': str(uuid.uuid4()), 'alarmDays': 'SatSun', 'alarmGroupName': 'private potty room'}
        with TasksRepository() as database:
            task_type = database.session.execute(select(ScheduledTaskTypes)).scalars().first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with pytest.raises(BadRequest):
            with TasksRepository() as database:
                database.update_schedule_task_by_user_id(self.USER_ID, new_task)

    def test_update_schedule_task_by_user__should_update_existing_record(self):
        new_task_type = 'turn on'
        new_task = {'taskId': self.TASK_ID, 'alarmDays': 'SatSun', 'alarmGroupName': 'private potty room', 'taskType': new_task_type, 'enabled':  False}
        with TasksRepository() as database:
            stmt = select(ScheduledTaskTypes).where(ScheduledTaskTypes.activity_name == 'turn off')
            task_type = database.session.execute(stmt).scalars().first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with TasksRepository() as database:
            database.update_schedule_task_by_user_id(self.USER_ID, new_task)

        with TasksRepository() as database:
            actual = database.session.execute(select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)).scalars().first()
            assert actual.alarm_days == 'SatSun'
            assert actual.alarm_group_name == 'private potty room'
            assert actual.id != self.TASK_ID
            assert actual.task_type.activity_name == new_task_type
            assert actual.enabled is False

    def test_delete_schedule_tasks_by_user__should_not_throw_when_record_does_not_exist(self):
        with TasksRepository() as database:
            database.delete_schedule_task_by_user(self.USER_ID, self.TASK_ID)

        with TasksRepository() as database:
            actual = database.session.execute(select(ScheduleTasks).where(ScheduleTasks.user_id == self.USER_ID)).first()
            assert actual is None


class TestDbPreferenceIntegration:
    USER_ID = str(uuid.uuid4())
    TASK_ID = str(uuid.uuid4())
    CITY = 'Praha'
    LIGHT_GROUP = '42'
    LIGHT_TIME = '02:22:22'
    GROUP_NAME = 'secret room'
    DAYS = 'MonTueWedThuFri'
    GARAGE = 'Jons'

    def setup_method(self):
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.TASK = ScheduleTasks(user_id=self.USER_ID, id=self.TASK_ID, alarm_light_group=self.LIGHT_GROUP, alarm_group_name=self.GROUP_NAME, alarm_days=self.DAYS, alarm_time=datetime.time.fromisoformat(self.LIGHT_TIME), enabled=True)
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY, garage_door=self.GARAGE, garage_id=1)
        with DatabaseBase() as database:
            database.session.add(self.USER)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(ScheduleTasks))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_preferences_by_user__should_return_preferences_for_valid_user(self):
        with AccountRepository() as database:
            response = database.get_preferences_by_user(self.USER_ID)

            assert response.tempUnit == 'fahrenheit'
            assert response.measureUnit == 'imperial'
            assert response.city == self.CITY
            assert response.isFahrenheit is True
            assert response.isImperial is True
            assert response.garageDoor == self.GARAGE
            assert response.garageId == 1

    def test_get_preferences_by_user__should_raise_bad_request_when_no_preferences(self):
        with pytest.raises(BadRequest):
            with AccountRepository() as database:
                bad_user_id = str(uuid.uuid4())
                database.get_preferences_by_user(bad_user_id)

    def test_insert_preferences_by_user__should_insert_valid_preferences(self):
        city = 'Vienna'
        new_door = 'Kalynns'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False, 'garageDoor': new_door, 'garageId': 5}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            database.session.commit()
            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.garage_door == new_door
            assert actual.garage_id == 5

    def test_insert_preferences_by_user__should_not_fail_when_time_is_none(self):
        city = 'Vienna'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False, 'garageDoor': 3}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True

    def test_insert_preferences_by_user__should_not_nullify_city_when_missing(self):
        preference_info = {'isFahrenheit': False, 'isImperial': True, 'garagaeDoor': 2}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == self.CITY
            assert actual.is_fahrenheit is False
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_is_fahrenheit_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isImperial': False, 'garageDoor': 1}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is False

    def test_insert_preferences_by_user__should_not_nullify_is_imperial_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'garageDoor': 1}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_garage_door_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE

    def test_insert_preferences_by_user__should_not_nullify_garage_id_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE
            assert actual.garage_id == 1

    def test_insert_preferences_by_user__should_set_garage_id_to_null_when_sent_null(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True, 'garageId': None}
        with AccountRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_door == self.GARAGE
            assert actual.garage_id is None
