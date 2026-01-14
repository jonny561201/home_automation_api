import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from mock import patch, mock
from sqlalchemy import orm
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.db.repositories.device_repository import DeviceRepository
from svc.db.models.user_information_model import UserRoles, Roles, UserPreference, RoleDevices, RoleDeviceNodes


class TestDeviceRepository:
    FAKE_USER = 'testName'
    FAKE_PASS = 'testPass'
    ROLE_NAME = 'garage_door'
    FIRST_NAME = 'John'
    LAST_NAME = 'Grape'
    USER_ID = '1234abcd'
    ROLE_ID = 'dcba4321'
    SESSION = None
    DATABASE = None
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = DeviceRepository()
        self.DATABASE.session = self.SESSION

    def test_add_new_role_device__should_call_add(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        self.SESSION.execute.return_value.unique.return_value.scalars.return_value.all.return_value = [role]
        self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        self.SESSION.add.assert_called()

    @patch('svc.db.repositories.device_repository.uuid')
    def test_add_new_role_device__should_return_device_id_in_response(self, mock_uuid):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        device_id = 'fake uuid string'
        mock_uuid.uuid4.return_value = device_id
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name=role_name))
        self.SESSION.execute.return_value.unique.return_value.scalars.return_value.all.return_value = [role]
        actual = self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

        assert actual == device_id

    def test_add_new_role_device__should_raise_unauthorized_when_no_role_returned(self):
        ip_address = '0.0.0.0'
        role_name = 'garage_door'
        role = UserRoles(user_id=str(uuid.uuid4()), role=Roles(role_name='security'))
        self.SESSION.query.return_value.filter_by.return_value.all.return_value = [role]
        with pytest.raises(Unauthorized):
            self.DATABASE.add_new_role_device(self.USER_ID, role_name, ip_address)

    def test_add_new_role_device__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.add_new_role_device(None, '', '')
        self.SESSION.query.assert_not_called()

    def test_add_new_device_node__should_call_add(self):
        node_name = 'test name'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = devices
        self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name, False)

        self.SESSION.add.assert_called()

    def test_add_new_device_node__should_query_user_preferences_by_user_id(self):
        node_name = 'Jons Door'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = devices
        self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name, True)

        assert self.SESSION.execute.return_value.scalars.return_value.first.call_count == 2

    def test_add_new_device_node__should_raise_unauthorized_if_no_user_pref(self):
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [devices, None]

        with pytest.raises(Unauthorized):
            self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, 'Jons Failure', True)

    def test_add_new_device_node__should_update_user_preference_door_and_id(self):
        node_name = 'Jons Door'
        pref = UserPreference(user_id=self.USER_ID)
        devices = RoleDevices(max_nodes=2, role_device_nodes=[RoleDeviceNodes()])
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [devices, pref]
        self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name, True)

        assert pref.garage_door == node_name
        assert pref.garage_id == 2

    def test_add_new_device_node__should_raise_unauthorized_when_device_id_not_match(self):
        node_name = 'test name'
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(Unauthorized):
            self.DATABASE.add_new_device_node(self.USER_ID, self.USER_ID, node_name, False)

    def test_add_new_device_node__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.add_new_device_node(None, self.USER_ID, '', True)
        self.SESSION.execute.assert_not_called()

    def test_add_new_device_node__should_return_the_number_of_node_positions_open(self):
        node_name = 'test name'
        devices = RoleDevices(max_nodes=2, role_device_nodes=[])
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = devices
        actual = self.DATABASE.add_new_device_node(self.USER_ID, self.ROLE_ID, node_name, None)

        assert actual.availableNodes == 1

    def test_get_user_garage_ip__should_raise_bad_request_error_when_no_user_role(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_garage_ip(self.USER_ID)

    def test_get_user_garage_ip__should_raise_bad_request_when_user_id_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_user_garage_ip(None)
        self.SESSION.execute.assert_not_called()

    def test_get_user_garage_ip__should_return_ip_address_of_user(self):
        ip_address = '1.1.1.1'
        device = RoleDevices(ip_address=ip_address, ip_port=None)
        role = UserRoles(user_id=self.USER_ID, role_devices=device, role=Roles(role_name='doesntMatter'))
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = role
        actual = self.DATABASE.get_user_garage_ip(self.USER_ID)

        assert actual == ip_address

    def test_get_user_garage_ip__should_return_ip_address_and_port_if_available(self):
        ip_address = '1.1.1.1'
        ip_port = 5001
        device = RoleDevices(ip_address=ip_address, ip_port=ip_port)
        role = UserRoles(user_id=self.USER_ID, role_devices=device, role=Roles(role_name='doesntMatter'))
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = role
        actual = self.DATABASE.get_user_garage_ip(self.USER_ID)

        assert actual == f'{ip_address}:{ip_port}'
