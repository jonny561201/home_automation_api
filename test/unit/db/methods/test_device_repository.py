import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from mock import mock
from sqlalchemy import orm
from werkzeug.exceptions import NotFound

from svc.models.devices import NodeInfo
from svc.db.models.user_information_model import Devices, DeviceType
from svc.db.repositories.device_repository import DeviceRepository


class TestDeviceRepository:
    USER_ID = '1234abcd'
    IP_ADDRESS = '0.0.0.0'
    IP_PORT = 8080
    DEVICE_NAME = 'garage_door'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = DeviceRepository()
        self.DATABASE.session = self.SESSION

    def test_add_new_device__should_call_add(self):
        self.DATABASE.add_new_device(self.USER_ID, self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

        self.SESSION.add.assert_called()

    def test_add_new_device__should_raise_not_found_when_user_not_found(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.add_new_device(self.USER_ID, self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT)

    def test_upsert_discovered_device__should_insert_new_device_when_not_found(self):
        device_type = DeviceType(id='type-id', type='garage_door')
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [device_type, None]

        self.DATABASE.upsert_discovered_device(self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT, 'api-key', 1, [], 'garage_door')

        self.SESSION.add.assert_called()

    def test_upsert_discovered_device__should_update_existing_device_ip(self):
        device_type = DeviceType(id='type-id', type='garage_door')
        existing = Devices(id='device-id', ip_address='10.0.0.1', ip_port=9999, name=self.DEVICE_NAME, device_type_id='type-id')
        existing.nodes = []
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [device_type, existing]

        self.DATABASE.upsert_discovered_device(self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT, 'api-key', 1, [], 'garage_door')

        assert existing.ip_address == self.IP_ADDRESS
        assert existing.ip_port == self.IP_PORT

    def test_upsert_discovered_device__should_return_existing_device_id_on_update(self):
        device_type = DeviceType(id='type-id', type='garage_door')
        existing = Devices(id='existing-id', ip_address='10.0.0.1', ip_port=9999, name=self.DEVICE_NAME, device_type_id='type-id')
        existing.nodes = []
        self.SESSION.execute.return_value.scalars.return_value.first.side_effect = [device_type, existing]

        actual = self.DATABASE.upsert_discovered_device(self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT, 'api-key', 1, [], 'garage_door')

        assert actual == 'existing-id'

    def test_upsert_discovered_device__should_raise_not_found_when_device_type_missing(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.upsert_discovered_device(self.DEVICE_NAME, self.IP_ADDRESS, self.IP_PORT, 'api-key', 1, [], 'garage_door')

    def test_get_device_address_info__should_raise_not_found_error_when_no_device(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None
        with pytest.raises(NotFound):
            self.DATABASE.get_device_info(self.USER_ID)

    def test_get_device_address_info__should_return_device_info(self):
        device = Devices(ip_address='1.1.1.1', ip_port=5000, api_key='test-key')
        device.nodes = []
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = device
        actual = self.DATABASE.get_device_info(self.USER_ID)

        assert actual.ip_address == '1.1.1.1'
        assert actual.ip_port == 5000
        assert actual.api_key == 'test-key'

    def test_get_device_address_info__should_return_node_names(self):
        from svc.db.models.user_information_model import DeviceNodes
        device = Devices(ip_address='1.1.1.1', ip_port=5000, api_key='test-key')
        node = DeviceNodes(node_device=1, node_name='Left Garage')
        device.nodes = [node]
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = device
        actual = self.DATABASE.get_device_info(self.USER_ID)

        assert actual.nodes == {'1': NodeInfo(name='Left Garage', nodeId=node.id)}

    def test_get_registered_devices__should_raise_not_found_when_user_id_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_registered_devices(None)

    def test_get_registered_devices__should_return_list_of_devices(self):
        expected = [Devices(ip_address='1.1.1.1', ip_port=1), Devices(ip_address='2.2.2.2', ip_port=2)]
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = expected
        actual = self.DATABASE.get_registered_devices(self.USER_ID)

        assert actual == expected

    def test_get_role_ids_by_device_ids__should_raise_not_found_when_user_id_is_none(self):
        with pytest.raises(NotFound):
            self.DATABASE.get_role_ids_by_device_ids(None, [])

    def test_get_role_ids_by_device_ids__should_return_role_ids_from_device_types(self):
        device_id_one = str(uuid.uuid4())
        device_id_two = str(uuid.uuid4())
        garage_type = DeviceType(auth0_role_id='role_garage')
        thermostat_type = DeviceType(auth0_role_id='role_thermo')
        device_one = Devices(id=device_id_one, user_id=self.USER_ID, device_type=garage_type)
        device_two = Devices(id=device_id_two, user_id=self.USER_ID, device_type=thermostat_type)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [device_one, device_two]

        actual = self.DATABASE.get_role_ids_by_device_ids(self.USER_ID, [device_id_one, device_id_two])

        assert sorted(actual) == ['role_garage', 'role_thermo']

    def test_get_role_ids_by_device_ids__should_skip_devices_without_role_id(self):
        device_id = str(uuid.uuid4())
        empty_type = DeviceType(auth0_role_id=None)
        device = Devices(id=device_id, user_id=self.USER_ID, device_type=empty_type)
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = [device]

        actual = self.DATABASE.get_role_ids_by_device_ids(self.USER_ID, [device_id])

        assert actual == []

    def test_get_device_id_by_api_key__should_return_device_id(self):
        device_id = str(uuid.uuid4())
        device = Devices(id=device_id, api_key='test-key')
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = device

        actual = self.DATABASE.get_device_id_by_api_key('test-key')

        assert actual == device_id

    def test_get_device_id_by_api_key__should_return_none_when_no_device(self):
        self.SESSION.execute.return_value.scalars.return_value.first.return_value = None

        actual = self.DATABASE.get_device_id_by_api_key('missing-key')

        assert actual is None


