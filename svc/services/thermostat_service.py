from datetime import datetime, time, timedelta

from svc.models.thermostat import ActiveTask, NextTask, ThermostatState
from svc.services import weather_request
from svc.utilities.conversion_utils import convert_to_fahrenheit
from svc.utilities.timezone_utils import now_in_timezone, weekday_label


def build_thermostat_state(internal_temp, state, is_fahrenheit, hvac_tasks, tz):
    desired_temp = __convert_desired_temp(is_fahrenheit, internal_temp, state)
    mode = state['mode']
    min_temp = 50.0 if is_fahrenheit else 10.0
    max_temp = 90.0 if is_fahrenheit else 32.0
    now_local = now_in_timezone(tz)
    enabled_tasks = __filter_enabled_hvac_tasks(hvac_tasks)
    active_task = __compute_active_task(enabled_tasks, now_local)
    next_task = __compute_next_task(enabled_tasks, now_local)
    current_desired = __compute_current_desired_temp(mode, active_task, enabled_tasks, now_local, min_temp, max_temp, desired_temp)
    return ThermostatState(
        currentTemp=internal_temp,
        isFahrenheit=is_fahrenheit,
        minThermostatTemp=min_temp,
        maxThermostatTemp=max_temp,
        mode=mode,
        desiredTemp=desired_temp,
        currentDesiredTemp=current_desired,
        activeTask=active_task,
        nextTask=next_task
    )


def get_forecast_for_preference(preference):
    if preference.latitude != None and preference.longitude != None:
        return weather_request.get_weather_by_coords(preference.latitude, preference.longitude, preference.tempUnit)
    return weather_request.get_weather_by_city(preference.city, preference.tempUnit, preference.state)


def get_extended_forecast_for_preference(preference, tz):
    if preference.latitude != None and preference.longitude != None:
        forecast = weather_request.get_extended_weather_by_coords(preference.latitude, preference.longitude, preference.tempUnit)
    else:
        forecast = weather_request.get_extended_weather_by_city(preference.city, preference.tempUnit, preference.state)
    __apply_localized_forecast_fields(forecast, tz)
    return forecast


def __convert_desired_temp(is_fahrenheit, internal_temp, state):
    desired_temp = state.get('desiredTemp')
    if desired_temp is None:
        return internal_temp
    elif is_fahrenheit:
        return convert_to_fahrenheit(desired_temp)
    else:
        return desired_temp


def __filter_enabled_hvac_tasks(hvac_tasks):
    return [task for task in hvac_tasks if task.enabled and task.taskType == 'hvac']


def __task_runs_on(task, weekday):
    return weekday in (task.alarmDays or '')


def __compute_active_task(enabled_tasks, now_local):
    today_label = weekday_label(now_local)
    for task in enabled_tasks:
        if task.hvacStart is None or task.hvacStop is None:
            continue
        if not __task_runs_on(task, today_label):
            continue
        start_dt = __combine_local(now_local, task.hvacStart)
        stop_dt = __combine_local(now_local, task.hvacStop)
        if start_dt < now_local < stop_dt:
            return ActiveTask(startTemp=task.hvacStartTemp, stopTemp=task.hvacStopTemp, stop=task.hvacStop[0:5])
    return None


def __compute_next_task(enabled_tasks, now_local):
    for offset in range(0, 8):
        candidate_day = now_local + timedelta(days=offset)
        label = weekday_label(candidate_day)
        day_matches = __tasks_starting_on(enabled_tasks, label)
        if offset == 0:
            day_matches = [task for task in day_matches if __combine_local(candidate_day, task.hvacStart) > now_local]
        if len(day_matches) == 0:
            continue
        soonest = min(day_matches, key=lambda task: task.hvacStart)
        day_label = 'Today' if offset == 0 else label
        return NextTask(startTemp=soonest.hvacStartTemp, start=soonest.hvacStart[0:5], dayLabel=day_label)
    return None


def __tasks_starting_on(enabled_tasks, weekday):
    return [task for task in enabled_tasks if task.hvacStart is not None and __task_runs_on(task, weekday)]


def __compute_current_desired_temp(mode, active_task, enabled_tasks, now_local, min_temp, max_temp, desired_temp):
    if mode != 'auto':
        return desired_temp
    if active_task is not None:
        return active_task.startTemp
    today_label = weekday_label(now_local)
    fallback = __first_today_stop_temp(enabled_tasks, today_label)
    if fallback is not None:
        return fallback
    return (min_temp + max_temp) / 2


def __first_today_stop_temp(enabled_tasks, today_label):
    for task in enabled_tasks:
        if __task_runs_on(task, today_label):
            return task.hvacStopTemp
    return None


def __combine_local(local_datetime, hms_string):
    parsed = time.fromisoformat(hms_string)
    return datetime(local_datetime.year, local_datetime.month, local_datetime.day,
                    parsed.hour, parsed.minute, parsed.second, tzinfo=local_datetime.tzinfo)


def __apply_localized_forecast_fields(forecast, tz):
    for entry in forecast.forecast:
        entry.day = __weekday_for_forecast_date(entry.date, tz)
        entry.high = int(round(entry.maxTemp))
        entry.low = int(round(entry.minTemp))


def __weekday_for_forecast_date(date_string, tz):
    if date_string in (None, ''):
        return None
    return weekday_label(datetime.fromisoformat(date_string).replace(tzinfo=tz))
