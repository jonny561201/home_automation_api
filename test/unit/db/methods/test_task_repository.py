import uuid
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest
from mock import mock, patch
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest

from db.models.user_information_model import ScheduleTasks, ScheduledTaskTypes
from svc.db.methods.tasks_repository import TasksRepository


class TestTaskRepository:
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = TasksRepository()
        self.DATABASE.session = self.SESSION


    @patch('svc.db.methods.tasks_repository.ScheduleTasks.__init__', return_value=None)
    def test_insert_schedule_task_by_user__should_create_task(self, mock_tasks):
        task = {'alarmLightGroup': '2', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon', 'enabled': False,
                'taskType': 'turn on', 'hvacMode': 'HEATING', 'hvacStart': '00:02:00', 'hvacStop': '01:00:01', 'hvacStartTemp': 20, 'hvacStopTemp': 16}
        task_type = ScheduledTaskTypes(activity_name='turn on')
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = task_type
        self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)

        mock_tasks.assert_called_with(user_id=self.USER_ID, alarm_light_group=task['alarmLightGroup'], alarm_time=time.fromisoformat(task['alarmTime']),
                                      alarm_group_name=task['alarmGroupName'], alarm_days=task['alarmDays'], task_type=task_type, enabled=task['enabled'],
                                      hvac_mode=task['hvacMode'], hvac_start=time.fromisoformat(task['hvacStart']), hvac_stop=time.fromisoformat(task['hvacStop']),
                                      hvac_start_temp=task['hvacStartTemp'], hvac_stop_temp=task['hvacStopTemp'])

    @patch('svc.db.methods.tasks_repository.ScheduleTasks.__init__', return_value=None)
    def test_insert_schedule_task_by_user__should_create_task_with_default_values_when_missing(self, mock_tasks):
        task = {'alarmLightGroup': '2', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon', 'enabled': False, 'taskType': 'turn on'}
        task_type = ScheduledTaskTypes(activity_name='turn on')
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = task_type
        self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)

        mock_tasks.assert_called_with(user_id=self.USER_ID, alarm_light_group=task['alarmLightGroup'], alarm_time=time.fromisoformat(task['alarmTime']),
                                      alarm_group_name=task['alarmGroupName'], alarm_days=task['alarmDays'], task_type=task_type, enabled=task['enabled'],
                                      hvac_mode=None, hvac_start=None, hvac_stop=None, hvac_start_temp=None, hvac_stop_temp=None)

    def test_insert_schedule_task_by_user__should_return_query_response_with_task_id(self):
        task = {'alarmLightGroup': '1', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon', 'enabled': True}
        task_id = uuid.uuid4()
        task_time = time.fromisoformat('00:01:01')
        new_task = ScheduleTasks(id=task_id, alarm_light_group='1', alarm_time=task_time, alarm_days='Mon', alarm_group_name='bathroom', task_type=ScheduledTaskTypes(), hvac_start=task_time, hvac_stop=task_time)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [new_task]
        actual = self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)

        assert actual.tasks[0].taskId == str(task_id)

    def test_insert_schedule_task_by_user__should_query_for_scheduled_task_type(self):
        task_type = 'all on'
        task = {'alarmLightGroup': '1', 'alarmGroupName': 'bathroom', 'alarmTime': '00:01:01', 'alarmDays': 'Mon', 'taskType': task_type, 'enabled': False}
        self.DATABASE.insert_schedule_task_by_user(self.USER_ID, task)
        self.SESSION.execute.return_value.scalars.return_value.first.assert_called()

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_alarm_days_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'taskType': 'all on', 'enabled': False}
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(self.USER_ID, preference_info)

    def test_insert_schedule_task_by_user__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.insert_schedule_task_by_user(None, {})
        self.SESSION.query.assert_not_called()

    def test_get_schedule_tasks_by_user__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_schedule_tasks_by_user(None, None)

    def test_get_schedule_tasks_by_user__should_query_database_for_tasks(self):
        self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)
        self.SESSION.execute.return_value.scalars.return_value.all.assert_called()

    def test_get_schedule_tasks_by_user_id__should_return_query_response(self):
        days = 'Sat'
        mode = 'HEAT'
        group_id = '1'
        group_name = 'Bedroom'
        group_time = '06:45:00'
        hvac_start = '08:45:00'
        hvac_stop = '07:45:00'
        hvac_start_temp = 20
        hvac_stop_temp = 16
        id = str(uuid.uuid4())
        task = ScheduleTasks(user_id=self.USER_ID, id=id, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time),
                             task_type=ScheduledTaskTypes(), hvac_mode=mode, hvac_start=time.fromisoformat(hvac_start), hvac_stop=time.fromisoformat(hvac_stop),
                             hvac_start_temp=hvac_start_temp, hvac_stop_temp=hvac_stop_temp)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)

        assert actual.tasks[0].alarmGroupName == group_name
        assert actual.tasks[0].alarmLightGroup == group_id
        assert actual.tasks[0].alarmDays == days
        assert actual.tasks[0].alarmTime == group_time
        assert actual.tasks[0].taskId == id
        assert actual.tasks[0].hvacMode == mode
        assert actual.tasks[0].hvacStart == hvac_start
        assert actual.tasks[0].hvacStop == hvac_stop
        assert actual.tasks[0].hvacStartTemp == hvac_start_temp
        assert actual.tasks[0].hvacStopTemp == hvac_stop_temp

    def test_get_schedule_tasks_by_user_id__should_return_matching_type_when_type_supplied(self):
        days = 'Sat'
        group_id = '1'
        group_name = 'Bedroom'
        group_time = '06:45:00'
        hvac_start = '08:45:00'
        hvac_stop = '07:45:00'
        mode = 'HEAT'
        task_type = 'hvac'
        id_one = str(uuid.uuid4())
        id_two = str(uuid.uuid4())
        task_one = ScheduleTasks(user_id=self.USER_ID, id=id_one, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time),
                             task_type=ScheduledTaskTypes(activity_name='sunrise alarm'), hvac_mode=mode, hvac_start=time.fromisoformat(hvac_start), hvac_stop=time.fromisoformat(hvac_stop))
        task_two = ScheduleTasks(user_id=self.USER_ID, id=id_two, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time),
                                 task_type=ScheduledTaskTypes(activity_name=task_type), hvac_mode=mode, hvac_start=time.fromisoformat(hvac_start), hvac_stop=time.fromisoformat(hvac_stop))
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task_one, task_two]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, task_type)

        assert len(actual.tasks) == 1
        assert actual.tasks[0].taskType == task_type

    def test_get_schedule_tasks_by_user_id__should_return_matching_type_case_insensitive_when_type_supplied(self):
        days = 'Sat'
        group_id = '1'
        group_name = 'Bedroom'
        group_time = '06:45:00'
        hvac_start = '08:45:00'
        hvac_stop = '07:45:00'
        mode = 'HEAT'
        task_type = 'hvac'
        id_one = str(uuid.uuid4())
        id_two = str(uuid.uuid4())
        task_one = ScheduleTasks(user_id=self.USER_ID, id=id_one, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time),
                             task_type=ScheduledTaskTypes(activity_name='sunrise alarm'), hvac_mode=mode, hvac_start=time.fromisoformat(hvac_start), hvac_stop=time.fromisoformat(hvac_stop))
        task_two = ScheduleTasks(user_id=self.USER_ID, id=id_two, alarm_light_group=group_id, alarm_group_name=group_name, alarm_days=days, alarm_time=time.fromisoformat(group_time),
                                 task_type=ScheduledTaskTypes(activity_name=task_type), hvac_mode=mode, hvac_start=time.fromisoformat(hvac_start), hvac_stop=time.fromisoformat(hvac_stop))
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task_one, task_two]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, 'HVAC')

        assert len(actual.tasks) == 1
        assert actual.tasks[0].taskType == task_type

    def test_get_schedule_tasks_by_user_id__should_return_task_activity_type(self):
        activity = 'turn all on'
        task_type = ScheduledTaskTypes(id=uuid.uuid4(), activity_name=activity)
        task = ScheduleTasks(id=id, alarm_time=time(), task_type=task_type, hvac_start=time(), hvac_stop=time())
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)

        assert actual.tasks[0].taskType == activity

    def test_get_schedule_tasks_by_user_id__should_return_none_when_no_alarm_time(self):
        activity = 'turn all on'
        task_type = ScheduledTaskTypes(id=uuid.uuid4(), activity_name=activity)
        task = ScheduleTasks(id=id, task_type=task_type, hvac_start=time(), hvac_stop=time())
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)

        assert actual.tasks[0].alarmTime is None

    def test_get_schedule_tasks_by_user_id__should_return_none_when_no_hvac_start_time(self):
        activity = 'turn all on'
        task_type = ScheduledTaskTypes(id=uuid.uuid4(), activity_name=activity)
        task = ScheduleTasks(id=id, task_type=task_type, alarm_time=time(), hvac_stop=time())
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)

        assert actual.tasks[0].hvacStart is None

    def test_get_schedule_tasks_by_user_id__should_return_none_when_no_hvac_stop_time(self):
        activity = 'turn all on'
        task_type = ScheduledTaskTypes(id=uuid.uuid4(), activity_name=activity)
        task = ScheduleTasks(id=id, task_type=task_type, alarm_time=time(), hvac_start=time())
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [task]
        actual = self.DATABASE.get_schedule_tasks_by_user(self.USER_ID, None)

        assert actual.tasks[0].hvacStop is None

    def test_update_schedule_task_by_user_id__should_query_for_user(self):
        task_id = 'asd123'
        task = {'taskId': task_id, 'alarmLightGroup': '1', 'alarmGroupName': 'jkasdhj', 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        self.SESSION.execute.return_value.scalars.return_value.first.assert_called()

    @patch('svc.db.methods.tasks_repository.uuid')
    def test_update_schedule_task_by_user_id__should_update_task_id(self, mock_uuid):
        task_id = 'asd123'
        task = {'taskId': task_id, 'alarmLightGroup': '1', 'alarmGroupName': 'asdf', 'alarmDays': 'Mon', 'alarmTime': '00:00', }
        new_task_id = uuid.uuid4()
        mock_uuid.uuid4.return_value = new_task_id
        existing_task = ScheduleTasks(user_id=self.USER_ID, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.user_id == self.USER_ID
        assert existing_task.id == str(new_task_id)

    def test_update_schedule_task_by_user_id__should_update_task_group_id(self):
        new_group_id = '1'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': new_group_id, 'alarmGroupName': 'test', 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_light_group='2', task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_light_group == new_group_id

    def test_update_schedule_task_by_user_id__should_update_task_group_name(self):
        group_name = 'doorwell'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': group_name, 'alarmDays': 'Mon', 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_group_name='potty', task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_group_name == group_name

    def test_update_schedule_task_by_user_id__should_update_task_days(self):
        days = 'MonTue'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': days, 'alarmTime': '00:00'}
        existing_task = ScheduleTasks(alarm_days='Wed', task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_days == days

    def test_update_schedule_task_by_user_id__should_update_task_time_as_date_object(self):
        alarm_time = '00:00:00'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': alarm_time}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_time == time.fromisoformat(alarm_time)

    def test_update_schedule_task_by_user_id__should_update_hvac_start_as_date_object(self):
        alarm_time = '00:00:00'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'hvacStart': alarm_time}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_start == time.fromisoformat(alarm_time)

    def test_update_schedule_task_by_user_id__should_update_hvac_stop_as_date_object(self):
        alarm_time = '00:00:00'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'hvacStop': alarm_time}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_stop == time.fromisoformat(alarm_time)

    def test_update_schedule_task_by_user_id__should_update_hvac_mode(self):
        mode = 'COOL'
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'hvacMode': mode}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_mode == mode

    def test_update_schedule_task_by_user_id__should_update_hvac_start_temp(self):
        temp = 22
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'hvacStartTemp': temp}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_start_temp == temp

    def test_update_schedule_task_by_user_id__should_update_hvac_stop_temp(self):
        temp = 22
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'hvacStopTemp': temp}
        existing_task = ScheduleTasks(alarm_light_group=time(), task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_stop_temp == temp

    def test_update_schedule_task_by_user_id__should_use_the_original_hvac_stop_temp_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon'}
        stop_temp = 18
        existing_task = ScheduleTasks(hvac_stop_temp=stop_temp, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_stop_temp == stop_temp

    def test_update_schedule_task_by_user_id__should_use_the_original_hvac_start_temp_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon'}
        start_temp = 18
        existing_task = ScheduleTasks(hvac_start_temp=start_temp, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_start_temp == start_temp

    def test_update_schedule_task_by_user_id__should_use_the_original_hvac_mode_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon'}
        mode = 'HEAT'
        existing_task = ScheduleTasks(hvac_mode=mode, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_mode == mode

    def test_update_schedule_task_by_user_id__should_use_the_original_hvac_stop_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon'}
        hvac_stop = time()
        existing_task = ScheduleTasks(hvac_stop=hvac_stop, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_stop == hvac_stop

    def test_update_schedule_task_by_user_id__should_use_the_original_hvac_start_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon'}
        hvac_start = time()
        existing_task = ScheduleTasks(hvac_start=hvac_start, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.hvac_start == hvac_start

    def test_update_schedule_task_by_user_id__should_use_the_original_light_group_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': '00:00:00'}
        group_id = '2'
        existing_task = ScheduleTasks(alarm_light_group=group_id, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_light_group == group_id

    def test_update_schedule_task_by_user_id__should_use_the_original_light_group_name_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmDays': 'Mon', 'alarmTime': '00:00:00'}
        room = 'potty'
        existing_task = ScheduleTasks(alarm_group_name=room, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_group_name == room

    def test_update_schedule_task_by_user_id__should_use_the_original_enabled_value_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmLightGroup': '3', 'alarmDays': 'Mon', 'alarmTime': '00:00:00'}
        enabled_value = False
        existing_task = ScheduleTasks(enabled=enabled_value, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.enabled == enabled_value

    def test_update_schedule_task_by_user_id__should_use_the_original_light_alarm_days_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmLightGroup': '3', 'alarmTime': '00:00:00'}
        days = 'SatSun'
        existing_task = ScheduleTasks(alarm_days=days, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_days == days

    def test_update_schedule_task_by_user_id__should_use_the_original_light_time_days_if_none(self):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmLightGroup': '3'}
        alarm_time = time()
        existing_task = ScheduleTasks(alarm_time=alarm_time, task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.alarm_time == alarm_time

    def test_update_schedule_task_by_user_id__should_updates_scheduled_task_type(self):
        task_type = 'sunrise alarm'
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': '00:00:00', 'taskType': task_type}
        existing_task = ScheduleTasks(task_type=ScheduledTaskTypes())
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [existing_task, ScheduledTaskTypes(activity_name=task_type)]
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert existing_task.task_type.activity_name == task_type

    def test_update_schedule_task_by_user_id__should_not_update_scheduled_task_type_when_matches_old(self):
        task_type = 'sunrise alarm'
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmDays': 'Mon', 'alarmTime': '00:00:00', 'taskType': task_type}
        existing_task = ScheduleTasks(task_type=ScheduledTaskTypes(activity_name=task_type))
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = existing_task
        self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert self.SESSION.execute.return_value.scalars.call_count == 1

    def test_update_schedule_task_by_user_id__should_raise_exception_when_query_returns_zero_records(self):
        task = {'task_id': 'absdf'}
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

    def test_update_schedule_task_by_user_id__should_raise_bad_request_when_user_id_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.update_schedule_task_by_user_id(None, {})
        self.SESSION.execute.assert_not_called()

    @patch('svc.db.methods.tasks_repository.uuid')
    def test_update_schedule_task_by_user_id__should_return_revised_task(self, mock_uuid):
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmLightGroup': '3', 'alarmTime': '00:00:00'}
        new_task_id = uuid.uuid4()
        mock_uuid.uuid4.return_value = new_task_id
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = ScheduleTasks(task_type=ScheduledTaskTypes())
        actual = self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert actual.taskId == str(new_task_id)

    def test_update_schedule_task_by_user_id__should_return_task_type_with_response(self):
        task_type = 'turn on'
        task = {'taskId': 'asdfasd', 'alarmGroupName': 'bedroom', 'alarmLightGroup': '3', 'alarmTime': '00:00:00', 'taskType': task_type}
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = ScheduleTasks(task_type=ScheduledTaskTypes(activity_name=task_type))
        actual = self.DATABASE.update_schedule_task_by_user_id(self.USER_ID, task)

        assert actual.taskType == task_type

    def test_delete_schedule_task_by_user__should_try_to_delete_record(self):
        task_id = str(uuid.uuid4())
        self.DATABASE.delete_schedule_task_by_user(self.USER_ID, task_id)
        self.SESSION.execute.assert_called()

    def test_delete_schedule_task_by_user__should_raise_bad_request_when_user_id_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_schedule_task_by_user(None, str(uuid.uuid4()))
        self.SESSION.execute.assert_not_called()
