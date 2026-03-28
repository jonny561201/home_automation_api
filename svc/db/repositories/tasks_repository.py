import uuid
from datetime import time

from sqlalchemy import select, delete
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import ScheduleTasks, ScheduledTaskTypes
from svc.db.repositories.database_base import DatabaseBase
from svc.models.app import Tasks, Task


class TasksRepository(DatabaseBase):

    def update_schedule_task_by_user_id(self, user_id, task):
        self._validate_property(user_id)
        stmt = select(ScheduleTasks).filter_by(user_id=user_id, id=task.get('taskId'))
        old_task = self.session.execute(stmt).scalars().first()
        self._validate_property(old_task)
        old_task.id = str(uuid.uuid4())
        old_task.alarm_days = task['alarmDays'] if task.get('alarmDays') else old_task.alarm_days
        old_task.alarm_time = time.fromisoformat(task['alarmTime']) if task.get('alarmTime') else old_task.alarm_time
        old_task.alarm_group_name = task['alarmGroupName'] if task.get('alarmGroupName') else old_task.alarm_group_name
        old_task.alarm_light_group = task['alarmLightGroup'] if task.get('alarmLightGroup') else old_task.alarm_light_group
        old_task.enabled = task['enabled'] if task.get('enabled') is not None else old_task.enabled
        old_task.hvac_start = time.fromisoformat(task['hvacStart']) if task.get('hvacStart') else old_task.hvac_start
        old_task.hvac_stop = time.fromisoformat(task['hvacStop']) if task.get('hvacStop') else old_task.hvac_stop
        old_task.hvac_mode = task['hvacMode'] if task.get('hvacMode') else old_task.hvac_mode
        old_task.hvac_start_temp = task['hvacStartTemp'] if task.get('hvacStartTemp') else old_task.hvac_start_temp
        old_task.hvac_stop_temp = task['hvacStopTemp'] if task.get('hvacStopTemp') else old_task.hvac_stop_temp

        if old_task.task_type.activity_name != task.get('taskType'):
            stmt = select(ScheduledTaskTypes).filter_by(activity_name=task.get('taskType'))
            old_task.task_type = self.session.execute(stmt).scalars().first()
        return self.__create_scheduled_task(old_task)

    def delete_schedule_task_by_user(self, user_id, task_id):
        self._validate_property(user_id)
        stmt = delete(ScheduleTasks).where(ScheduleTasks.user_id == user_id, ScheduleTasks.id == task_id)
        self.session.execute(stmt)

    def get_schedule_tasks_by_user(self, user_id, task_type):
        self._validate_property(user_id)
        stmt = select(ScheduleTasks).filter_by(user_id=user_id)
        tasks = self.session.execute(stmt).scalars().all()
        if task_type is not None:
            return Tasks(tasks=[self.__create_scheduled_task(task) for task in tasks if task.task_type.activity_name == task_type.lower()])
        return Tasks(tasks=[self.__create_scheduled_task(task) for task in tasks])

    def insert_schedule_task_by_user(self, user_id, task):
        self._validate_property(user_id)
        try:
            alarm_time = None if task.get('alarmTime') is None else time.fromisoformat(task.get('alarmTime'))
            hvac_start = None if task.get('hvacStart') is None else time.fromisoformat(task.get('hvacStart'))
            hvac_stop = None if task.get('hvacStop') is None else time.fromisoformat(task.get('hvacStop'))
            stmt = select(ScheduledTaskTypes).filter_by(activity_name=task.get('taskType'))
            task_type = self.session.execute(stmt).scalars().first()
            new_task = ScheduleTasks(user_id=user_id, alarm_light_group=task.get('alarmLightGroup'), alarm_days=task['alarmDays'],
                                     alarm_group_name=task.get('alarmGroupName'), alarm_time=alarm_time, task_type=task_type, enabled=task['enabled'],
                                     hvac_mode=task.get('hvacMode'), hvac_start=hvac_start, hvac_stop=hvac_stop,
                                     hvac_start_temp=task.get('hvacStartTemp'), hvac_stop_temp=task.get('hvacStopTemp'))
            self.session.add(new_task)
        except KeyError:
            raise NotFound
        stmt = select(ScheduleTasks).where(ScheduleTasks.user_id==user_id)
        new_tasks = self.session.execute(stmt).scalars().all()
        return Tasks(tasks=[self.__create_scheduled_task(task) for task in new_tasks])

    @staticmethod
    def __create_scheduled_task(task):
        alarm_time = None if task.alarm_time is None else task.alarm_time.isoformat()
        hvac_start = None if task.hvac_start is None else task.hvac_start.isoformat()
        hvac_stop = None if task.hvac_stop is None else task.hvac_stop.isoformat()
        return Task(alarmDays=task.alarm_days, alarmTime=alarm_time, alarmGroupName=task.alarm_group_name, alarmLightGroup=task.alarm_light_group,
                    hvacMode=task.hvac_mode, hvacStart=hvac_start, hvacStop=hvac_stop, hvacStartTemp=task.hvac_start_temp, hvacStopTemp=task.hvac_stop_temp,
                    taskId=str(task.id), enabled=task.enabled, taskType=task.task_type.activity_name)
