import uuid

import pytest
from sqlalchemy import select, delete
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import UserPreference, Devices, UserInformation, ChildAccounts, DeviceType
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.device_repository import DeviceRepository


class TestDbDeviceIntegration:
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    IP_ADDRESS = '192.175.7.9'

    def setup_method(self):
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='steve', last_name='rogers')
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=False)
        with DatabaseBase() as database:
            stmt = select(DeviceType).where(DeviceType.type == 'Garage Door')
            self.DEVICE_TYPE = database.session.execute(stmt).scalars().first()
            self.DEVICE = Devices(ip_address=self.IP_ADDRESS, node_name='test', user_id=self.USER_ID, device_type_id=self.DEVICE_TYPE.id)
            database.session.add_all([self.USER_INFO, self.CHILD_USER])
            database.session.add(self.USER_PREF)
            database.session.commit()
            database.session.add(self.DEVICE)
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(Devices))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID))

            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))

    def test_add_new_device__should_raise_not_found_when_no_user_found(self):
        role_name = 'garage_door'
        ip_address = '0.0.0.0'
        with pytest.raises(NotFound):
            with DeviceRepository() as database:
                database.add_new_device(str(uuid.uuid4()), role_name, ip_address)

    def test_add_new_device__should_insert_a_new_device_into_table(self):
        ip_address = '192.168.1.145'
        node_name = 'sample test name'
        with DeviceRepository() as database:
            database.add_new_device(self.USER_ID, node_name, ip_address)

            actual = database.session.execute(select(Devices).where(Devices.node_name == node_name)).scalars().first()
            assert actual.ip_address == ip_address
            assert str(actual.user_id) == self.USER_ID

    def test_add_new_device__should_register_new_device_to_parent_from_child(self):
        ip_address = '192.168.1.145'
        with DeviceRepository() as database:
            device_id = database.add_new_device(self.CHILD_USER_ID, 'other name', ip_address)

            actual = database.session.execute(select(Devices).where(Devices.id == device_id)).scalars().first()

            assert actual.ip_address == ip_address

    def test_get_user_garage_ip__should_return_garage_ip(self):
        with DeviceRepository() as database:
            actual = database.get_user_garage_ip(self.USER_ID)

            assert actual == self.IP_ADDRESS

    def test_get_user_garage_ip__should_raise_not_found_when_no_user_id_match(self):
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_user_garage_ip(str(uuid.uuid4()))

    def test_get_user_garage_ip__should_raise_not_found_when_no_device(self):
        with DeviceRepository() as database:
            database.session.execute(delete(Devices).where(Devices.user_id == self.USER_ID))
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_user_garage_ip(str(uuid.uuid4()))
