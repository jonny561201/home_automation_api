import uuid

from mock import patch

from svc.constants.home_automation import Automation
from svc.models.app import Preference, Task, Tasks
from svc.services.hvac_schedule_service import publish_hvac_schedule


@patch('svc.services.hvac_schedule_service.publish')
@patch('svc.services.hvac_schedule_service.UserRepository')
@patch('svc.services.hvac_schedule_service.TasksRepository')
class TestPublishHvacSchedule:
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        self.TASK = Task(alarmDays='MonTue', alarmGroupName=None, alarmLightGroup=None, enabled=True, hvacMode='HEAT',
                         hvacStartTemp=72, hvacStopTemp=62, taskId=str(uuid.uuid4()), taskType='hvac', hvacStart='06:00:00', hvacStop='22:00:00')
        self.FAHRENHEIT = Preference(city='Austin', tempUnit='fahrenheit', measureUnit='imperial')
        self.CELSIUS = Preference(city='Austin', tempUnit='celsius', measureUnit='metric')

    def __arrange(self, mock_tasks, mock_user, tasks, preference):
        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.return_value = Tasks(tasks=tasks)
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = preference

    def test_publish_hvac_schedule__should_load_hvac_tasks_for_user(self, mock_tasks, mock_user, mock_publish):
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        mock_tasks.return_value.__enter__.return_value.get_schedule_tasks_by_user.assert_called_with(self.USER_ID, 'hvac')

    def test_publish_hvac_schedule__should_publish_schedule_action_to_hvac_queue(self, mock_tasks, mock_user, mock_publish):
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        expected_task = {'taskId': self.TASK.taskId, 'alarmDays': 'MonTue', 'hvacStart': '06:00:00', 'hvacStop': '22:00:00',
                         'hvacStartTemp': 72, 'hvacStopTemp': 62, 'hvacMode': Automation.HVAC.MODE.HEATING}
        mock_publish.assert_called_with(Automation.HVAC.QUEUE, {'action': 'schedule', 'tasks': [expected_task]})

    def test_publish_hvac_schedule__should_convert_temps_to_celsius_for_fahrenheit_users(self, mock_tasks, mock_user, mock_publish):
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.FAHRENHEIT)

        publish_hvac_schedule(self.USER_ID)

        published = mock_publish.call_args.args[1]['tasks'][0]
        assert published['hvacStartTemp'] == 22.22
        assert published['hvacStopTemp'] == 16.67

    def test_publish_hvac_schedule__should_exclude_disabled_tasks(self, mock_tasks, mock_user, mock_publish):
        self.TASK.enabled = False
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        mock_publish.assert_called_with(Automation.HVAC.QUEUE, {'action': 'schedule', 'tasks': []})

    def test_publish_hvac_schedule__should_not_raise_when_broker_unavailable(self, mock_tasks, mock_user, mock_publish):
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)
        mock_publish.side_effect = Exception('Broker Unavailable')

        publish_hvac_schedule(self.USER_ID)

    def test_publish_hvac_schedule__should_send_cooling_when_task_mode_is_cool(self, mock_tasks, mock_user, mock_publish):
        self.TASK.hvacMode = 'COOL'
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        assert mock_publish.call_args.args[1]['tasks'][0]['hvacMode'] == Automation.HVAC.MODE.COOLING

    def test_publish_hvac_schedule__should_send_auto_when_task_mode_is_empty(self, mock_tasks, mock_user, mock_publish):
        self.TASK.hvacMode = ''
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        assert mock_publish.call_args.args[1]['tasks'][0]['hvacMode'] == Automation.HVAC.MODE.AUTO

    def test_publish_hvac_schedule__should_send_auto_when_task_mode_is_none(self, mock_tasks, mock_user, mock_publish):
        self.TASK.hvacMode = None
        self.__arrange(mock_tasks, mock_user, [self.TASK], self.CELSIUS)

        publish_hvac_schedule(self.USER_ID)

        assert mock_publish.call_args.args[1]['tasks'][0]['hvacMode'] == Automation.HVAC.MODE.AUTO
