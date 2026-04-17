import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import Unauthorized, BadRequest, NotFound

from svc.db.repositories.user_repository import UserRepository
from svc.db.models.user_information_model import DeviceNodes, UserInformation, UserPreference


class TestCredentialRepository:
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = UserRepository()
        self.DATABASE.session = self.SESSION
    def test_get_user_info__should_return_the_matching_user_info(self):
        user = UserInformation(id=self.USER_ID, first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = user

        actual = self.DATABASE.get_user_info(self.USER_ID)

        assert actual['user_id'] == self.USER_ID
        assert actual['first_name'] == self.FIRST_NAME
        assert actual['last_name'] == self.LAST_NAME

    def test_get_user_info__should_raise_unauthorized_if_user_is_none(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(Unauthorized):
            self.DATABASE.get_user_info('123abc')

    def test_insert_preferences_by_user__should_raise_bad_request_when_preferences_empty(self):
        preference_info = {}
        user_id = uuid.uuid4()
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(user_id, preference_info)
            self.SESSION.execute.return_value.scalars.assert_not_called()

    def test_insert_preferences_by_user__should_raise_bad_request_when_no_user_id(self):
        with pytest.raises(BadRequest):
            self.DATABASE.insert_preferences_by_user(None, {'isFahrenheit': True})
        self.SESSION.execute.assert_not_called()

    def test_insert_preferences_by_user__should_not_throw_when_city_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_fahrenheit_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_is_imperial_missing(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_garage_door(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_id': 1, 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)

    def test_insert_preferences_by_user__should_not_throw_when_garage_id(self):
        preference_info = {'alarmGroupName': 'bedroom', 'alarmLightGroup': '1', 'alarmTime': '00:01:00', 'alarmDays': 'Mon', 'garage_door': 'test'}
        user_id = str(uuid.uuid4())
        self.DATABASE.insert_preferences_by_user(user_id, preference_info)


class TestPreference:
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = UserRepository()
        self.DATABASE.session = self.SESSION

    def test_get_preferences_by_user__should_return_user_temp_preferences(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit is 'celsius'

    def test_get_preferences_by_user__should_return_user_temp_preferences_with_fahrenheit(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, is_fahrenheit=True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit is 'fahrenheit'

    def test_get_preferences_by_user__should_return_user_city_preferences(self):
        city = 'London'
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, city)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.city == city

    def test_get_preferences_by_user__should_return_temp_unit_fahrenheit(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City', True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit == 'fahrenheit'

    def test_get_preferences_by_user__should_return_temp_unit_celsius(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City', False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.tempUnit == 'celsius'

    def test_get_preferences_by_user__should_return_measure_unit_preferences(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City', True, True)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.measureUnit == 'imperial'

    def test_get_preferences_by_user__should_return_measure_unit_preferences_for_metric(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference

        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.measureUnit == 'metric'

    def test_get_preferences_by_user__should_throw_not_found_when_no_preferences(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None

        with pytest.raises(NotFound):
            self.DATABASE.get_preferences_by_user(uuid.uuid4().hex)

    def test_get_preferences_by_user__should_throw_not_found_when_user_id_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_preferences_by_user(None)

        self.SESSION.execute.assert_not_called()

    def test_get_preferences_by_user__should_return_garage_node_id(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City', True, False)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference
        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.garageNodeId is None

    def test_get_preferences_by_user__should_return_garage_node_name(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        node_id = str(uuid.uuid4())
        node = DeviceNodes(id=node_id, node_name='Left Garage')
        preference = TestPreference.__create_user_preference(user, 'Fake City')
        preference.garage_node_id = node_id
        preference.garage_node = node
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference
        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.garageNodeName == 'Left Garage'

    def test_get_preferences_by_user__should_return_none_garage_node_name_when_no_node(self):
        user = UserInformation(first_name=self.FIRST_NAME, last_name=self.LAST_NAME)
        preference = TestPreference.__create_user_preference(user, 'Fake City')
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = preference
        actual = self.DATABASE.get_preferences_by_user(uuid.uuid4())

        assert actual.garageNodeName is None

    @staticmethod
    def __create_user_preference(user, city='Moline', is_fahrenheit=False, is_imperial=False):
        preference = UserPreference()
        preference.user = user
        preference.city = city
        preference.is_fahrenheit = is_fahrenheit
        preference.is_imperial = is_imperial
        preference.alarm_light_group = '2'
        preference.alarm_time = datetime.now().time()
        preference.alarm_days = 'MonTueWedThuFri'
        preference.alarm_group_name = 'bedroom'
        preference.garage_node_id = None

        return preference
