import datetime
import uuid

import pytest
from sqlalchemy import delete, select
from werkzeug.exceptions import NotFound, Unauthorized

from svc.db.models.user_information_model import UserInformation, ScheduleTasks, UserPreference, Devices, DeviceNodes, DeviceType
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.user_repository import UserRepository


class TestUserIntegration:
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
            database.session.commit()
            device_type = database.session.execute(select(DeviceType).where(DeviceType.type == 'garage_door')).scalars().first()
            self.DEVICE = Devices(user_id=self.USER_ID, ip_address='1.1.1.1', name='test-device', api_key='test-key', device_type_id=device_type.id)
            database.session.add(self.DEVICE)
            database.session.flush()
            self.DEVICE_NODE = DeviceNodes(device_id=self.DEVICE.id, node_device=1, node_name='Left Garage')
            database.session.add(self.DEVICE_NODE)
            database.session.flush()
            self.NODE_ID = str(self.DEVICE_NODE.id)
            database.session.add(self.USER_PREFERENCES)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(ScheduleTasks))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(DeviceNodes))
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_preferences_by_user__should_return_preferences_for_valid_user(self):
        with UserRepository() as database:
            response = database.get_preferences_by_user(self.USER_ID)

            assert response.tempUnit == 'fahrenheit'
            assert response.measureUnit == 'imperial'
            assert response.city == self.CITY
            assert response.tempUnit == 'fahrenheit'
            assert response.measureUnit == 'imperial'
            assert response.garageNodeId is None

    def test_get_preferences_by_user__should_raise_not_found_when_no_preferences(self):
        with pytest.raises(NotFound):
            with UserRepository() as database:
                bad_user_id = str(uuid.uuid4())
                database.get_preferences_by_user(bad_user_id)

    def test_insert_preferences_by_user__should_insert_valid_preferences(self):
        city = 'Vienna'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info, self.NODE_ID)
            database.session.commit()
            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert str(actual.garage_node_id) == self.NODE_ID

    def test_insert_preferences_by_user__should_not_fail_when_time_is_none(self):
        city = 'Vienna'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': False}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)
            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True

    def test_insert_preferences_by_user__should_not_nullify_city_when_missing(self):
        preference_info = {'isFahrenheit': False, 'isImperial': True}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == self.CITY
            assert actual.is_fahrenheit is False
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_is_fahrenheit_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isImperial': False}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is False

    def test_insert_preferences_by_user__should_not_nullify_is_imperial_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True

    def test_insert_preferences_by_user__should_not_nullify_garage_door_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_node_id is None

    def test_insert_preferences_by_user__should_not_nullify_garage_id_when_missing(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_node_id is None

    def test_insert_preferences_by_user__should_set_garage_id_to_null_when_sent_null(self):
        city = 'Lisbon'
        preference_info = {'city': city, 'isFahrenheit': True, 'isImperial': True, 'garageNodeId': None}
        with UserRepository() as database:
            database.insert_preferences_by_user(self.USER_ID, preference_info)

            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()

            assert actual.city == city
            assert actual.is_fahrenheit is True
            assert actual.is_imperial is True
            assert actual.garage_node_id is None


class TestDbCredentialIntegration:
    FIRST = 'Jon'
    LAST = 'Test'
    USER_ID = str(uuid.uuid4())

    def setup_method(self):
        self.USER = UserInformation(id=self.USER_ID, first_name=self.FIRST, last_name=self.LAST)
        with DatabaseBase() as database:
            database.session.add(self.USER)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_user_info__should_return_user_information(self):
        with UserRepository() as database:
            actual = database.get_user_info(self.USER_ID)

            assert actual['user_id'] == self.USER_ID
            assert actual['first_name'] == self.FIRST
            assert actual['last_name'] == self.LAST

    def test_get_user_info__should_raise_unauthorized_when_user_not_found(self):
        with pytest.raises(Unauthorized):
            with UserRepository() as database:
                missing_user_id = str(uuid.uuid4())
                database.get_user_info(missing_user_id)