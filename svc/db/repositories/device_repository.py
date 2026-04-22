import uuid

from sqlalchemy import select

from svc.models.devices import DeviceInfo, NodeInfo
from svc.db.models.user_information_model import ChildAccounts, DeviceNodes, DeviceType, UserInformation, Devices
from svc.db.repositories.database_base import DatabaseBase


class DeviceRepository(DatabaseBase):

    def get_registered_devices(self, user_id):
        self._validate_property(user_id)
        stmt = select(Devices).filter_by(user_id=user_id)
        return self.session.execute(stmt).scalars().all()

    def get_all_devices(self):
        stmt = select(Devices)
        return self.session.execute(stmt).scalars().all()

    def is_child_user(self, user_id):
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        return self.session.execute(stmt).scalars().first() is not None

    def add_new_device(self, user_id, name, ip_address, ip_port):
        user_stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(user_stmt).scalars().first()
        self._validate_property(user)

        type_stmt = select(DeviceType).filter_by(type='garage_door')
        device_type = self.session.execute(type_stmt).scalars().first()

        device = Devices(id=str(uuid.uuid4()), user_id=user_id, ip_address=ip_address, ip_port=ip_port, name=name, api_key=str(uuid.uuid4()), device_type_id=device_type.id, registered=False)
        self.session.add(device)
        return device.id

    def upsert_discovered_device(self, name, ip_address, ip_port, api_key, max_nodes, nodes, device_type_name):
        device_type = self._get_device_type(device_type_name)
        existing = self._get_device_by_name(name, device_type.id)
        if existing:
            existing.ip_address = ip_address
            existing.ip_port = ip_port
            existing.max_nodes = max_nodes
            self._upsert_device_nodes(existing.id, nodes)
            return existing.id
        device = Devices(ip_address=ip_address, ip_port=ip_port, name=name, device_type_id=device_type.id, registered=False, api_key=api_key, max_nodes=max_nodes)
        self.session.add(device)
        self.session.flush()
        self._upsert_device_nodes(device.id, nodes)
        return device.id

    def get_device_info(self, device_type: str):
        stmt = select(Devices).where(Devices.device_type.has(DeviceType.type == device_type))
        device = self.session.execute(stmt).scalars().first()
        self._validate_property(device)
        nodes = {str(n.node_device): NodeInfo(name=n.node_name, nodeId=n.id) for n in device.nodes}
        return DeviceInfo(id=str(device.id), ip_address=device.ip_address, ip_port=device.ip_port, api_key=device.api_key, nodes=nodes)

    def register_device_to_user(self, device_id, user_id, nodes):
        self._validate_property(user_id)
        device_stmt = select(Devices).filter_by(id=device_id)
        device = self.session.execute(device_stmt).scalars().first()
        self._validate_property(device)
        user_stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(user_stmt).scalars().first()
        self._validate_property(user)
        device.user_id = user_id
        device.registered = True
        self._upsert_device_nodes(device_id, nodes)
        return device.id

    def get_node_id_by_device(self, device_id, node_device):
        stmt = select(DeviceNodes).where(DeviceNodes.device_id == device_id, DeviceNodes.node_device == node_device)
        node = self.session.execute(stmt).scalars().first()
        self._validate_property(node)
        return str(node.id)

    def get_role_ids_by_device_ids(self, user_id, device_ids):
        self._validate_property(user_id)
        stmt = select(Devices).where(Devices.user_id == user_id, Devices.id.in_(device_ids))
        devices = self.session.execute(stmt).scalars().all()
        role_ids = []
        for device in devices:
            if device.device_type and device.device_type.auth0_role_id:
                role_ids.append(device.device_type.auth0_role_id)
        return role_ids

    def get_device_id_by_api_key(self, api_key):
        stmt = select(Devices).filter_by(api_key=api_key)
        device = self.session.execute(stmt).scalars().first()
        return str(device.id) if device else None

    def _get_device_type(self, type_name):
        stmt = select(DeviceType).filter_by(type=type_name)
        device_type = self.session.execute(stmt).scalars().first()
        self._validate_property(device_type)
        return device_type

    def _get_device_by_name(self, name, device_type_id):
        stmt = select(Devices).where(Devices.name == name, Devices.device_type_id == device_type_id)
        return self.session.execute(stmt).scalars().first()

    def _upsert_device_nodes(self, device_id, nodes):
        for node in nodes:
            stmt = select(DeviceNodes).where(DeviceNodes.device_id == device_id, DeviceNodes.node_device == node['nodeDevice'])
            existing = self.session.execute(stmt).scalars().first()
            if existing:
                existing.node_name = node['nodeName']
            else:
                self.session.add(DeviceNodes(device_id=device_id, node_device=node['nodeDevice'], node_name=node['nodeName']))

