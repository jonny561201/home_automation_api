import uuid

from sqlalchemy import select

from svc.db.models.user_information_model import DeviceType, UserInformation
from svc.db.models.user_information_model import Devices
from svc.db.repositories.database_base import DatabaseBase


class DeviceRepository(DatabaseBase):

    def get_registered_devices(self, user_id):
        self._validate_property(user_id)
        stmt = select(Devices).filter_by(user_id=user_id)
        return self.session.execute(stmt).scalars().all()

    def add_new_device(self, user_id, name, ip_address, ip_port):
        user_stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(user_stmt).scalars().first()
        self._validate_property(user)

        type_stmt = select(DeviceType).filter_by(type='garage_door')
        device_type = self.session.execute(type_stmt).scalars().first()

        device = Devices(id=str(uuid.uuid4()), user_id=user_id, ip_address=ip_address, ip_port=ip_port, node_name=name, device_type_id=device_type.id, registered=False)
        self.session.add(device)
        return device.id

    def upsert_discovered_device(self, name, ip_address, ip_port):
        device_type = self._get_device_type('garage_door')
        existing = self._get_device_by_name(name, device_type.id)
        if existing:
            existing.ip_address = ip_address
            existing.ip_port = ip_port
            return existing.id
        device = Devices(ip_address=ip_address, ip_port=ip_port, node_name=name, device_type_id=device_type.id, registered=False)
        self.session.add(device)
        return device.id

    def get_user_garage_ip(self, user_id):
        stmt = select(Devices).where(Devices.user_id == user_id, Devices.device_type.has(DeviceType.type == 'garage_door'))
        device = self.session.execute(stmt).scalars().first()
        self._validate_property(device)
        if device.ip_port is None:
            return device.ip_address
        return f'{device.ip_address}:{device.ip_port}'

    #TODO: I think this is dead
    def get_role_ids_by_device_ids(self, user_id, device_ids):
        self._validate_property(user_id)
        stmt = select(Devices).where(Devices.user_id == user_id, Devices.id.in_(device_ids))
        devices = self.session.execute(stmt).scalars().all()
        role_ids = []
        for device in devices:
            if device.device_type and device.device_type.auth0_role_id:
                role_ids.append(device.device_type.auth0_role_id)
        return role_ids

    def _get_device_type(self, type_name):
        stmt = select(DeviceType).filter_by(type=type_name)
        device_type = self.session.execute(stmt).scalars().first()
        self._validate_property(device_type)
        return device_type

    def _get_device_by_name(self, name, device_type_id):
        stmt = select(Devices).where(Devices.node_name == name, Devices.device_type_id == device_type_id)
        return self.session.execute(stmt).scalars().first()
