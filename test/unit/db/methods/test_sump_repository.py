import uuid

import pytest
from mock import mock
from sqlalchemy import orm
from werkzeug.exceptions import NotFound

from svc.db.repositories.sump_repository import SumpRepository


class TestSumpDatabase:
    DEVICE_ID = '1234abcd'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = SumpRepository()
        self.DATABASE.session = self.SESSION


    def test_get_current_sump_level_by_device__should_raise_not_found_error_when_missing_record(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.get_current_sump_level_by_device(uuid.uuid4().hex)

    def test_get_current_sump_level_by_device__should_raise_not_found_when_device_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_current_sump_level_by_device(None)
        self.SESSION.execute.assert_not_called()

    def test_get_average_sump_level_by_device__should_raise_not_found_error_when_no_records(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.get_average_sump_level_by_device('12345')

    def test_get_average_sump_level_by_device__should_raise_not_found_when_device_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_average_sump_level_by_device(None)
        self.SESSION.execute.assert_not_called()

    def test_insert_current_sump_level__should_call_add(self):
        device_id = 1234
        depth_info = {'datetime': None,
                      'warning_level': 1,
                      'depth': None}
        self.DATABASE.insert_current_sump_level(device_id, depth_info)

        self.SESSION.add.assert_called()

    def test_insert_current_sump_level__should_raise_not_found_when_depth_info_none(self):
        depth_info = None
        device_id = 1234
        with pytest.raises(NotFound):
            self.DATABASE.insert_current_sump_level(device_id, depth_info)

    def test_insert_current_sump_level__should_raise_not_found_when_device_id_is_none(self):
        depth_info = {'datetime': None,
                      'warning_level': 1,
                      'depth': None}
        with pytest.raises(NotFound):
            self.DATABASE.insert_current_sump_level(None, depth_info)
        self.SESSION.add.assert_not_called()

    def test_insert_current_sump_level__should_raise_not_found_when_depth_info_missing_keys(self):
        depth_info = {'badKey': 1234}
        device_id = 1234
        with pytest.raises(NotFound):
            self.DATABASE.insert_current_sump_level(device_id, depth_info)
