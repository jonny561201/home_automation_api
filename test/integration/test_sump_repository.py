import uuid
from datetime import datetime

import pytest
from sqlalchemy import select, delete
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import DailySumpPumpLevel, AverageSumpPumpLevel, ChildAccounts, \
    UserInformation
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.sump_repository import SumpDatabase


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
        self.FIRST_SUMP_DAILY = DailySumpPumpLevel(id=88, distance=11.0, user_id=self.FIRST_USER_ID, warning_level=2, create_date=self.DATE)
        self.SECOND_SUMP_DAILY = DailySumpPumpLevel(id=99, distance=self.DEPTH, user_id=self.SECOND_USER_ID, warning_level=1, create_date=self.DATE)
        self.THIRD_SUMP_DAILY = DailySumpPumpLevel(id=100, distance=12.0, user_id=self.SECOND_USER_ID, warning_level=2, create_date=self.DATE)
        self.FIRST_SUMP_AVG = AverageSumpPumpLevel(id=34, user_id=self.FIRST_USER_ID, distance=12.0, create_day=self.DAY)
        self.SECOND_SUMP_AVG = AverageSumpPumpLevel(id=35, user_id=self.FIRST_USER_ID, distance=self.DEPTH, create_day=self.DAY)
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.FIRST_USER_ID, child_user_id=self.CHILD_USER_ID)

        with DatabaseBase() as database:
            database.session.add_all([self.FIRST_USER, self.SECOND_USER, self.CHILD_USER])
            database.session.add_all([self.FIRST_SUMP_AVG, self.SECOND_SUMP_AVG])
            database.session.add_all([self.FIRST_SUMP_DAILY, self.SECOND_SUMP_DAILY, self.THIRD_SUMP_DAILY])
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 88))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 99))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.id == 100))
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.user_id == self.FIRST_USER_ID, DailySumpPumpLevel.distance == self.UPDATED_DEPTH))
            database.session.execute(delete(AverageSumpPumpLevel).where(AverageSumpPumpLevel.id == 34))
            database.session.execute(delete(AverageSumpPumpLevel).where(AverageSumpPumpLevel.id == 35))

            database.session.execute(delete(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.FIRST_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.SECOND_USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))


    def test_get_current_sump_level_by_user__should_return_valid_sump_level(self):
        with SumpDatabase() as database:
            actual = database.get_current_sump_level_by_user(self.FIRST_USER_ID)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with SumpDatabase() as database:
            actual = database.get_current_sump_level_by_user(self.SECOND_USER_ID)
            assert actual['currentDepth'] == 12.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_return_parent_records_for_child(self):
        with SumpDatabase() as database:
            actual = database.get_current_sump_level_by_user(self.CHILD_USER_ID)
            assert actual['currentDepth'] == 11.0
            assert actual['warningLevel'] == 2

    def test_get_current_sump_level_by_user__should_raise_not_found_when_user_not_found(self):
        with SumpDatabase() as database:
            with pytest.raises(NotFound):
                database.get_current_sump_level_by_user(str(uuid.uuid4()))

    def test_get_average_sump_level_by_user__should_return_latest_record_for_single_user(self):
        with SumpDatabase() as database:
            actual = database.get_average_sump_level_by_user(self.FIRST_USER_ID)
            assert actual == {'averageDepth': self.DEPTH, 'latestDate': self.DAY}

    def test_get_average_sump_level_by_user__should_return_parent_records_for_child(self):
        with SumpDatabase() as database:
            actual = database.get_average_sump_level_by_user(self.CHILD_USER_ID)
            assert actual == {'averageDepth': self.DEPTH, 'latestDate': self.DAY}

    def test_get_average_sump_level_by_user__should_raise_not_found_when_user_not_found(self):
        with SumpDatabase() as database:
            with pytest.raises(NotFound):
                database.get_average_sump_level_by_user(str(uuid.uuid4()))

    def test_insert_current_sump_level__should_store_new_record(self):
        with SumpDatabase() as database:
            depth_info = {'depth': self.UPDATED_DEPTH,
                          'warning_level': 3,
                          'datetime': str(self.DATE)}
            database.insert_current_sump_level(self.FIRST_USER_ID, depth_info)

            stmt = select(DailySumpPumpLevel).where(DailySumpPumpLevel.user_id == self.FIRST_USER_ID, DailySumpPumpLevel.distance == self.UPDATED_DEPTH)
            actual = database.session.execute(stmt).scalars().first()

            assert float(actual.distance) == self.UPDATED_DEPTH

    def test_insert_current_sump_level__should_raise_not_found_with_bad_data(self):
        depth_info = {'badData': None}
        user_id = 1234
        with pytest.raises(NotFound):
            with SumpDatabase() as database:
                database.insert_current_sump_level(user_id, depth_info)

