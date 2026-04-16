import uuid
from datetime import datetime

import pytest
from sqlalchemy import select, delete
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import ChildAccounts, DailySumpPumpLevel, AverageSumpPumpLevel, \
    UserInformation, Devices, DeviceType
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.sump_repository import SumpRepository


class TestDbSumpIntegration:
    DEPTH = 8.0
    UPDATED_DEPTH = 12.123
    FIRST_USER_ID = str(uuid.uuid4())
    SECOND_USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    DAY = datetime.date(datetime.now())
    DATE = datetime.now()

    def setup_method(self):
        self.FIRST_USER = UserInformation(id=self.FIRST_USER_ID, first_name='Jon', last_name='Test')
        self.SECOND_USER = UserInformation(id=self.SECOND_USER_ID, first_name='Dylan', last_name='Fake')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.FIRST_USER_ID, child_user_id=self.CHILD_USER_ID)

        with DatabaseBase() as database:
            stmt = select(DeviceType).where(DeviceType.type == 'sump_pump')
            device_type = database.session.execute(stmt).scalars().first()

            database.session.add_all([self.FIRST_USER, self.SECOND_USER, self.CHILD_USER])
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

            self.FIRST_DEVICE = Devices(ip_address='1.1.1.1', ip_port=5001, name='sump-first', api_key='key1',
                                        user_id=self.FIRST_USER_ID, device_type_id=device_type.id, registered=True)
            self.SECOND_DEVICE = Devices(ip_address='2.2.2.2', ip_port=5002, name='sump-second', api_key='key2',
                                         user_id=self.SECOND_USER_ID, device_type_id=device_type.id, registered=True)
            database.session.add_all([self.FIRST_DEVICE, self.SECOND_DEVICE])
            database.session.flush()

            self.FIRST_DEVICE_ID = str(self.FIRST_DEVICE.id)
            self.SECOND_DEVICE_ID = str(self.SECOND_DEVICE.id)

            self.FIRST_SUMP_DAILY = DailySumpPumpLevel(id=88, distance=11.0, device_id=self.FIRST_DEVICE.id, warning_level=2, create_date=self.DATE)
            self.SECOND_SUMP_DAILY = DailySumpPumpLevel(id=99, distance=self.DEPTH, device_id=self.SECOND_DEVICE.id, warning_level=1, create_date=self.DATE)
            self.THIRD_SUMP_DAILY = DailySumpPumpLevel(id=100, distance=12.0, device_id=self.SECOND_DEVICE.id, warning_level=2, create_date=self.DATE)
            self.FIRST_SUMP_AVG = AverageSumpPumpLevel(id=34, device_id=self.FIRST_DEVICE.id, distance=12.0, create_day=self.DAY)
            self.SECOND_SUMP_AVG = AverageSumpPumpLevel(id=35, device_id=self.FIRST_DEVICE.id, distance=self.DEPTH, create_day=self.DAY)

            database.session.add_all([self.FIRST_SUMP_AVG, self.SECOND_SUMP_AVG])
            database.session.add_all([self.FIRST_SUMP_DAILY, self.SECOND_SUMP_DAILY, self.THIRD_SUMP_DAILY])

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 88))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 99))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 100))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.device_id == self.FIRST_DEVICE.id, DailySumpPumpLevel.distance == self.UPDATED_DEPTH))
            database.session.execute(delete(AverageSumpPumpLevel).where(AverageSumpPumpLevel.id == 34))
            database.session.execute(delete(AverageSumpPumpLevel).where(AverageSumpPumpLevel.id == 35))

            database.session.execute(delete(Devices).where(Devices.user_id == self.FIRST_USER_ID))
            database.session.execute(delete(Devices).where(Devices.user_id == self.SECOND_USER_ID))
            database.session.execute(delete(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.FIRST_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.SECOND_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))


    def test_get_current_sump_level_by_device__should_return_valid_sump_level(self):
        with SumpRepository() as database:
            actual = database.get_current_sump_level_by_device(self.FIRST_DEVICE_ID)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_device__should_return_latest_record_for_single_device(self):
        with SumpRepository() as database:
            actual = database.get_current_sump_level_by_device(self.SECOND_DEVICE_ID)
            assert actual['currentDepth'] == 12.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_device__should_raise_not_found_when_device_not_found(self):
        with SumpRepository() as database:
            with pytest.raises(NotFound):
                database.get_current_sump_level_by_device(str(uuid.uuid4()))

    def test_get_average_sump_level_by_device__should_return_latest_record_for_single_device(self):
        with SumpRepository() as database:
            actual = database.get_average_sump_level_by_device(self.FIRST_DEVICE_ID)
            assert actual == {'averageDepth': self.DEPTH, 'latestDate': self.DAY}

    def test_get_average_sump_level_by_device__should_raise_not_found_when_device_not_found(self):
        with SumpRepository() as database:
            with pytest.raises(NotFound):
                database.get_average_sump_level_by_device(str(uuid.uuid4()))

    def test_insert_current_sump_level__should_store_new_record(self):
        with SumpRepository() as database:
            depth_info = {'depth': self.UPDATED_DEPTH,
                          'warning_level': 3,
                          'datetime': str(self.DATE)}
            database.insert_current_sump_level(self.FIRST_DEVICE_ID, depth_info)

            stmt = select(DailySumpPumpLevel).where(DailySumpPumpLevel.device_id == self.FIRST_DEVICE.id, DailySumpPumpLevel.distance == self.UPDATED_DEPTH)
            actual = database.session.execute(stmt).scalars().first()

            assert float(actual.distance) == self.UPDATED_DEPTH

    def test_insert_current_sump_level__should_raise_not_found_with_bad_data(self):
        depth_info = {'badData': None}
        device_id = 1234
        with pytest.raises(NotFound):
            with SumpRepository() as database:
                database.insert_current_sump_level(device_id, depth_info)

    def test_get_sump_device_id_by_user__should_return_device_for_parent_user(self):
        with SumpRepository() as database:
            actual = database.get_sump_device_id_by_user(self.FIRST_USER_ID)

            assert actual == self.FIRST_DEVICE_ID

    def test_get_sump_device_id_by_user__should_resolve_child_to_parent_device(self):
        with SumpRepository() as database:
            actual = database.get_sump_device_id_by_user(self.CHILD_USER_ID)

            assert actual == self.FIRST_DEVICE_ID

    def test_get_sump_device_id_by_user__should_raise_not_found_when_no_sump_device(self):
        with SumpRepository() as database:
            with pytest.raises(NotFound):
                database.get_sump_device_id_by_user(str(uuid.uuid4()))
