import uuid

import pytest
from sqlalchemy import select, delete
from werkzeug.exceptions import BadRequest, Unauthorized, NotFound

from svc.db.models.user_information_model import UserPreference, RoleDevices, RoleDeviceNodes, UserInformation, Roles, \
    UserRoles, ChildAccounts
from svc.db.repositories.database_base import DatabaseBase
from svc.db.repositories.device_repository import DeviceRepository


class TestDbDeviceIntegration:
    USER_ID = str(uuid.uuid4())
    CHILD_USER_ID = str(uuid.uuid4())
    ROLE_ID = str(uuid.uuid4())
    USER_ROLE_ID = str(uuid.uuid4())
    ROLE_NAME = "lighting"

    def setup_method(self):
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='steve', last_name='rogers')
        self.ROLE = Roles(id=self.ROLE_ID, role_desc="lighting", role_name=self.ROLE_NAME)
        self.USER_ROLE = UserRoles(id=self.USER_ROLE_ID, user_id=self.USER_ID, role_id=self.ROLE_ID, role=self.ROLE)
        self.CHILD_USER = UserInformation(id=self.CHILD_USER_ID, first_name='Kalynn', last_name='Dawn')
        self.CHILD_ACCOUNT = ChildAccounts(parent_user_id=self.USER_ID, child_user_id=self.CHILD_USER_ID)
        self.USER_PREF = UserPreference(user_id=self.USER_ID, is_fahrenheit=True, is_imperial=False)
        with DatabaseBase() as database:
            database.session.add(self.ROLE)
            database.session.add_all([self.USER_INFO, self.CHILD_USER])
            database.session.add(self.USER_ROLE)
            database.session.add(self.USER_PREF)
            database.session.commit()
            database.session.add(self.CHILD_ACCOUNT)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(RoleDeviceNodes))
            database.session.execute(delete(RoleDevices))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(ChildAccounts).where(ChildAccounts.child_user_id == self.CHILD_USER_ID))
            database.session.execute(delete(UserRoles).where(UserRoles.id == self.USER_ROLE_ID))

            database.session.execute(delete(Roles).where(Roles.id == self.ROLE_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.CHILD_USER_ID))

    def test_add_new_device__should_raise_unauthorized_when_no_role_found(self):
        role_name = 'garage_door'
        ip_address = '0.0.0.0'
        with pytest.raises(Unauthorized):
            with DeviceRepository() as database:
                database.add_new_role_device(self.USER_ID, role_name, ip_address)

    def test_add_new_device__should_insert_a_new_device_into_table(self):
        ip_address = '192.168.1.145'
        with DeviceRepository() as database:
            database.add_new_role_device(self.USER_ID, self.ROLE_NAME, ip_address)

            actual = database.session.execute(select(RoleDevices).where(RoleDevices.user_role_id == self.USER_ROLE_ID)).scalars().first()
            assert actual.ip_address == ip_address

    def test_add_new_device__should_register_new_device_to_parent_from_child(self):
        ip_address = '192.168.1.145'
        with DeviceRepository() as database:
            device_id = database.add_new_role_device(self.CHILD_USER_ID, self.ROLE_NAME, ip_address)

            actual = database.session.execute(select(RoleDevices).where(RoleDevices.id == device_id)).scalars().first()

            assert actual.ip_address == ip_address

    def test_add_new_device_node__should_raise_unauthorized_when_no_device_found(self):
        ip_address = '1.1.1.1'
        device_id = str(uuid.uuid4())
        node_name = 'test node'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            with pytest.raises(Unauthorized):
                database.add_new_device_node(self.USER_ID, str(uuid.uuid4()), node_name, False)

    def test_add_new_device_node__should_insert_a_new_node_into_table(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actual = database.session.execute(select(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == device_id)).scalars().first()
            assert actual.node_name == node_name
            database.session.delete(actual)

    def test_add_new_device_node__should_return_available_nodes_left(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            actual = database.add_new_device_node(self.USER_ID, device_id, node_name, False)
            assert actual.availableNodes == 1

    def test_add_new_device_node__should_set_node_device_to_one_when_first_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'first garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actual = database.session.execute(select(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == device_id)).scalars().first()
            assert actual.node_device == 1

    def test_add_new_device_node__should_set_node_device_to_two_when_second_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'second garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            node = RoleDeviceNodes(node_name='test', node_device=1, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actuals = database.session.execute(select(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == device_id)).scalars().all()
            assert len(actuals) == 2
            assert [actual.node_device for actual in actuals] == [1,2]

    def test_add_new_device_node__should_set_node_device_to_three_when_third_node(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'third garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=3, ip_address=ip_address)
            node_one = RoleDeviceNodes(node_name='test 1', node_device=1, role_device_id=device_id)
            node_two = RoleDeviceNodes(node_name='test 2', node_device=2, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node_one)
            database.session.add(node_two)
            database.session.commit()
            database.add_new_device_node(self.USER_ID, device_id, node_name, False)

            actuals = database.session.execute(select(RoleDeviceNodes).where(RoleDeviceNodes.role_device_id == device_id)).scalars().all()
            assert len(actuals) == 3
            assert [actual.node_device for actual in actuals] == [1,2,3]

    def test_add_new_device_node__should_raise_bad_request_when_exceeding_max_nodes(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        node_name = 'third garage door'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            node_one = RoleDeviceNodes(node_name='test 1', node_device=1, role_device_id=device_id)
            node_two = RoleDeviceNodes(node_name='test 2', node_device=2, role_device_id=device_id)
            database.session.add(device)
            database.session.add(node_one)
            database.session.add(node_two)

            with pytest.raises(BadRequest):
                database.add_new_device_node(self.USER_ID, device_id, node_name, False)

    def test_add_new_device_node__should_update_preference_when_flag_set_to_true(self):
        device_id = str(uuid.uuid4())
        node_name = 'Jons New'
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address='1.1.1.1')
            database.session.add(device)
            database.add_new_device_node(self.USER_ID, device_id, node_name, True)

        with DeviceRepository() as database:
            actual = database.session.execute(select(UserPreference).where(UserPreference.user_id == self.USER_ID)).scalars().first()
            assert actual.garage_door == node_name
            assert actual.garage_id == 1

    def test_get_user_garage_ip__should_return_garage_ip(self):
        ip_address = '192.175.7.9'
        device_id = str(uuid.uuid4())
        with DeviceRepository() as database:
            device = RoleDevices(id=device_id, user_role_id=self.USER_ROLE_ID, max_nodes=2, ip_address=ip_address)
            database.session.add(device)

            actual = database.get_user_garage_ip(self.USER_ID)

            assert actual == ip_address

    def test_get_user_garage_ip__should_raise_not_found_when_not_found(self):
        with DeviceRepository() as database:
            with pytest.raises(NotFound):
                database.get_user_garage_ip(str(uuid.uuid4()))
