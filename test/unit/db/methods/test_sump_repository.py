import uuid

import pytest
from mock import mock
from sqlalchemy import orm
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import ChildAccounts, Devices
from svc.db.repositories.sump_repository import SumpRepository


class TestSumpDatabase:
    DEVICE_ID = '1234abcd'
    USER_ID = 'user5678'

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

    def test_insert_average_sump_level__should_call_add(self):
        device_id = 1234
        depth_info = {'depth': None}
        self.DATABASE.insert_average_sump_level(device_id, depth_info)

        self.SESSION.add.assert_called()

    def test_insert_average_sump_level__should_raise_not_found_when_depth_info_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.insert_average_sump_level(1234, None)

    def test_insert_average_sump_level__should_raise_not_found_when_device_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.insert_average_sump_level(None, {'depth': None})
        self.SESSION.add.assert_not_called()

    def test_insert_average_sump_level__should_raise_not_found_when_depth_info_missing_keys(self):
        with pytest.raises(NotFound):
            self.DATABASE.insert_average_sump_level(1234, {'badKey': 1234})

    def test_get_sump_device_id_by_user__should_return_device_id_for_parent_user(self):
        device_id = str(uuid.uuid4())
        sump_device = Devices(id=device_id, user_id=self.USER_ID)
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, sump_device]

        actual = self.DATABASE.get_sump_device_id_by_user(self.USER_ID)

        assert actual == device_id

    def test_get_sump_device_id_by_user__should_resolve_child_to_parent_device(self):
        parent_user_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        child_account = ChildAccounts(child_user_id=self.USER_ID, parent_user_id=parent_user_id)
        sump_device = Devices(id=device_id, user_id=parent_user_id)
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [child_account, sump_device]

        actual = self.DATABASE.get_sump_device_id_by_user(self.USER_ID)

        assert actual == device_id

    def test_get_sump_device_id_by_user__should_raise_not_found_when_no_device(self):
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [None, None]
        with pytest.raises(NotFound):
            self.DATABASE.get_sump_device_id_by_user(self.USER_ID)

    def test_get_sump_device_id_by_user__should_raise_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_sump_device_id_by_user(None)
