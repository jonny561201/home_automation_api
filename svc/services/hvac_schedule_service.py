import logging

from svc.constants.home_automation import Automation
from svc.db.repositories.tasks_repository import TasksRepository
from svc.db.repositories.user_repository import UserRepository
from svc.utilities.conversion_utils import convert_to_celsius
from svc.utilities.rabbitmq_client import publish


def publish_hvac_schedule(user_id):
    with TasksRepository() as database:
        tasks = database.get_schedule_tasks_by_user(user_id, 'hvac')
    with UserRepository() as database:
        preferences = database.get_preferences_by_user(user_id)
    is_fahrenheit = preferences.tempUnit == 'fahrenheit'
    schedule = [__build_schedule_task(task, is_fahrenheit) for task in tasks.tasks if task.enabled]
    try:
        publish(Automation.HVAC.QUEUE, {'action': 'schedule', 'tasks': schedule})
    except Exception as exc:
        logging.warning(f'Failed to publish hvac schedule: {exc}')


def __build_schedule_task(task, is_fahrenheit):
    return {
        'taskId': task.taskId,
        'alarmDays': task.alarmDays,
        'hvacStart': task.hvacStart,
        'hvacStop': task.hvacStop,
        'hvacStartTemp': __to_celsius(task.hvacStartTemp, is_fahrenheit),
        'hvacStopTemp': __to_celsius(task.hvacStopTemp, is_fahrenheit),
        'hvacMode': __to_device_mode(task.hvacMode)
    }


def __to_celsius(temp, is_fahrenheit):
    if temp is None or not is_fahrenheit:
        return temp
    return convert_to_celsius(temp)


def __to_device_mode(hvac_mode):
    if hvac_mode == 'HEAT':
        return Automation.HVAC.MODE.HEATING
    if hvac_mode == 'COOL':
        return Automation.HVAC.MODE.COOLING
    return Automation.HVAC.MODE.AUTO
