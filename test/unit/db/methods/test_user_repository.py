import uuid

import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.db.repositories.user_repository import UserRepository
from svc.db.models.user_information_model import UserInformation


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