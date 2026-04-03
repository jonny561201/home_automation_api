from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from mock import patch, mock
from sqlalchemy import orm
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import Devices
from svc.db.repositories.device_repository import DeviceRepository


class TestDeviceRepository:
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = DeviceRepository()
        self.DATABASE.session = self.SESSION

    def test_add_new_device__should_call_add(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        self.DATABASE.add_new_device(self.USER_ID, role_name, ip_address)

        self.SESSION.add.assert_called()

    @patch('svc.db.repositories.device_repository.uuid')
    def test_add_new_device__should_return_device_id_in_response(self, mock_uuid):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        device_id = 'fake uuid string'
        mock_uuid.uuid4.return_value = device_id
        actual = self.DATABASE.add_new_device(self.USER_ID, role_name, ip_address)

        assert actual == device_id

    def test_add_new_device__should_raise_not_found_when_user_id_is_none(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.add_new_device(None, '', '')
        self.SESSION.query.assert_not_called()

    def test_get_user_garage_ip__should_raise_not_found_error_when_no_user_role(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.get_user_garage_ip(self.USER_ID)

    def test_get_user_garage_ip__should_return_ip_address_of_user(self):
        ip_address = '1.1.1.1'
        device = Devices(ip_address=ip_address, ip_port=None)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = device
        actual = self.DATABASE.get_user_garage_ip(self.USER_ID)

        assert actual == ip_address

    def test_get_user_garage_ip__should_return_ip_address_and_port_if_available(self):
        ip_address = '1.1.1.1'
        ip_port = 5001
        device = Devices(ip_address=ip_address, ip_port=ip_port)
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = device
        actual = self.DATABASE.get_user_garage_ip(self.USER_ID)

        assert actual == f'{ip_address}:{ip_port}'

    def test_get_registered_devices__should_raise_not_found_when_user_id_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_registered_devices(None)

    def test_get_registered_devices__should_return_list_of_devices(self):
        expected = [Devices(ip_address='1.1.1.1', ip_port=1), Devices(ip_address='2.2.2.2', ip_port=2)]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = expected
        actual = self.DATABASE.get_registered_devices(self.USER_ID)

        assert actual == expected