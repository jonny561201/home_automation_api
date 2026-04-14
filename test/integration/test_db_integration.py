import datetime
import uuid

import pytest
from sqlalchemy import delete, select
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import UserInformation, UserPreference, ScheduleTasks, ScheduledTaskTypes
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.tasks_repository import TasksRepository
from svc.models.app import Tasks


class TestDbTaskIntegration:
    USER_ID = str(uuid.uuid4())
    TASK_ID = str(uuid.uuid4())
    CITY = 'Praha'
    LIGHT_GROUP = '42'
    LIGHT_TIME = '02:22:22'
    GROUP_NAME = 'secret room'
    DAYS = 'MonTueWedThuFri'

    def setup_method(self):

        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        self.TASK = ScheduleTasks(user_id=self.USER_ID, id=self.TASK_ID, alarm_light_group=self.LIGHT_GROUP, alarm_group_name=self.GROUP_NAME, alarm_days=self.DAYS, alarm_time=datetime.time.fromisoformat(self.LIGHT_TIME), enabled=True)
        self.USER_PREFERENCES = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=True, city=self.CITY)
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

    def test_update_schedule_task_by_user__should_raise_not_found_when_user_does_not_exist(self):
        new_task = {'taskId': str(uuid.uuid4()), 'alarmDays': 'SatSun', 'alarmGroupName': 'private potty room'}
        with TasksRepository() as database:
            task_type = database.session.execute(select(ScheduledTaskTypes)).scalars().first()
            self.TASK.task_type = task_type
            database.session.add(self.TASK)

        with pytest.raises(NotFound):
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
