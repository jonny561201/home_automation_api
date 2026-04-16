import uuid

import pytest
from sqlalchemy import select, delete
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import UserPreference, Devices, DeviceNodes, UserInformation, ChildAccounts, DeviceType
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.device_repository import DeviceRepository


class TestDbDeviceIntegration:
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    IP_ADDRESS = '192.175.7.9'
    PORT = 5000
    TYPE = 'garage_door'

    def setup_method(self):
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='steve', last_name='rogers')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=False)
        with DatabaseBase() as database:
            stmt = select(DeviceType).where(DeviceType.type == self.TYPE)
            self.DEVICE_TYPE = database.session.execute(stmt).scalars().first()
            self.DEVICE = Devices(ip_address=self.IP_ADDRESS, ip_port=self.PORT, name='test', api_key='test-key', user_id=self.USER_ID, device_type_id=self.DEVICE_TYPE.id)
            database.session.add_all([self.USER_INFO, self.CHILD_USER])
            database.session.add(self.USER_PREF)
            database.session.commit()
            database.session.add(self.DEVICE)
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DeviceNodes))
            database.session.execute(delete(Devices))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID))

            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))

    def test_add_new_device__should_raise_not_found_when_no_user_found(self):
        with pytest.raises(NotFound):
            with DeviceRepository() as database:
                database.add_new_device(str(uuid.uuid4()), 'garage_door', '0.0.0.0', 5000)

    def test_add_new_device__should_insert_a_new_device_into_table(self):
        ip_address = '192.168.1.145'
        port = 5000
        device_name = 'sample test name'
        with DeviceRepository() as database:
            database.add_new_device(self.USER_ID, device_name, ip_address, port)

            actual = database.session.execute(select(Devices).where(Devices.name == device_name)).scalars().first()
            assert actual.ip_address == ip_address
            assert actual.ip_port == port
            assert str(actual.user_id) == self.USER_ID

    def test_add_new_device__should_register_new_device_to_parent_from_child(self):
        ip_address = '192.168.1.145'
        port = 4000
        with DeviceRepository() as database:
            device_id = database.add_new_device(self.CHILD_USER_ID, 'other name', ip_address, port)

            actual = database.session.execute(select(Devices).where(Devices.id == device_id)).scalars().first()

            assert actual.ip_address == ip_address
            assert actual.ip_port == port

    def test_get_device_info__should_return_device_info(self):
        with DeviceRepository() as database:
            actual = database.get_device_info(self.TYPE)

            assert actual.ip_address == self.IP_ADDRESS
            assert actual.ip_port == self.PORT

    def test_get_device_info__should_raise_not_found_when_no_type_match(self):
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_device_info(str(uuid.uuid4()))

    def test_get_device_info__should_raise_not_found_when_no_device(self):
        with DeviceRepository() as database:
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_device_info(str(uuid.uuid4()))

    def test_get_registered_devices__should_return_all_user_devices(self):
        with DeviceRepository() as database:
            actual = database.get_registered_devices(self.USER_ID)

            assert len(actual) == 1
            assert actual[0].ip_address == self.IP_ADDRESS
            assert actual[0].name == 'test'

    def test_get_registered_devices__should_return_empty_list_when_no_devices(self):
        with DeviceRepository() as database:
            actual = database.get_registered_devices(self.CHILD_USER_ID)

            assert actual == []

    def test_get_device_id_by_api_key__should_return_device_id(self):
        with DeviceRepository() as database:
            actual = database.get_device_id_by_api_key('test-key')

            assert actual == str(self.DEVICE.id)

    def test_get_device_id_by_api_key__should_return_none_when_not_found(self):
        with DeviceRepository() as database:
            actual = database.get_device_id_by_api_key('nonexistent-key')

            assert actual is None

    def test_get_sump_device_id_by_user__should_return_device_for_parent_user(self):
        with DatabaseBase() as database:
            sump_type = database.session.execute(select(DeviceType).where(DeviceType.type == 'sump_pump')).scalars().first()
            sump_device = Devices(ip_address='3.3.3.3', ip_port=5001, name='sump-test', api_key='sump-key',
                                  user_id=self.USER_ID, device_type_id=sump_type.id, registered=True)
            database.session.add(sump_device)
            database.session.flush()
            expected_id = str(sump_device.id)

        with DeviceRepository() as database:
            actual = database.get_sump_device_id_by_user(self.USER_ID)

            assert actual == expected_id

    def test_get_sump_device_id_by_user__should_resolve_child_to_parent_device(self):
        with DatabaseBase() as database:
            sump_type = database.session.execute(select(DeviceType).where(DeviceType.type == 'sump_pump')).scalars().first()
            sump_device = Devices(ip_address='4.4.4.4', ip_port=5002, name='sump-parent', api_key='sump-parent-key',
                                  user_id=self.USER_ID, device_type_id=sump_type.id, registered=True)
            database.session.add(sump_device)
            database.session.flush()
            expected_id = str(sump_device.id)

        with DeviceRepository() as database:
            actual = database.get_sump_device_id_by_user(self.CHILD_USER_ID)

            assert actual == expected_id

    def test_get_sump_device_id_by_user__should_raise_not_found_when_no_sump_device(self):
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_sump_device_id_by_user(self.CHILD_USER_ID)