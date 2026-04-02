import uuid

from sqlalchemy import select
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import ChildAccounts, UserRoles, RoleDevices, RoleDeviceNodes, UserPreference
from svc.models.device import DoorDeviceDetails, DeviceNode


class DeviceRepository(DatabaseBase):

    def add_new_role_device(self, user_id, role_name, ip_address):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id

        stmt = select(UserRoles).filter_by(user_id=select_user_id)
        user_roles = self.session.execute(stmt).unique().scalars().all()
        role = next((user_role for user_role in user_roles if user_role.role.role_name == role_name), None)
        if role is None:
            raise Unauthorized
        device_id = uuid.uuid4()
        device = Devices(id=str(device_id), ip_address=ip_address, max_nodes=2, user_role_id=role.id)
        self.session.add(device)
        return str(device_id)

    def add_new_device_node(self, user_id, device_id, node_name, preferred):
        self._validate_property(user_id)
        stmt = select(Devices).filter_by(id=device_id)
        device = self.session.execute(stmt).scalars().first()
        if device is None:
            raise Unauthorized
        node_size = len(device.role_device_nodes)
        if preferred:
            self.__update_preference(node_name, node_size, user_id)
        if node_size >= device.max_nodes:
            raise BadRequest
        node = RoleDeviceNodes(node_name=node_name, role_device_id=device_id, node_device=node_size + 1)
        self.session.add(node)

        door_device = DoorDeviceDetails(doorId=node.node_device, doorName=node.node_name)
        return DeviceNode(availableNodes=device.max_nodes - (node_size + 1), device=door_device)

    def get_user_garage_ip(self, user_id):
        self._validate_property(user_id)
        stmt = select(UserRoles).filter_by(user_id=user_id)
        user_role = self.session.execute(stmt).scalars().first()
        self._validate_property(user_role)
        if user_role.role_devices.ip_port is None:
            return user_role.role_devices.ip_address
        return f'{user_role.role_devices.ip_address}:{user_role.role_devices.ip_port}'

    def __update_preference(self, node_name, node_size, user_id):
        stmt = select(UserPreference).filter_by(user_id=user_id)
        preference = self.session.execute(stmt).scalars().first()
        if preference is None:
            raise Unauthorized
        preference.garage_id = node_size + 1
        preference.garage_door = node_name