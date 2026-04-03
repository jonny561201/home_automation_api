import uuid

from sqlalchemy import select
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.db.models.user_information_model import DeviceType, UserInformation
from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import ChildAccounts, Devices, UserPreference
from svc.models.devices import DoorDeviceDetails, DeviceNode


class DeviceRepository(DatabaseBase):

    def get_registered_devices(self, user_id):
        self._validate_property(user_id)
        stmt = select(Devices).filter_by(user_id=user_id)
        return self.session.execute(stmt).scalars().all()

    def add_new_device(self, user_id, name, ip_address):
        user_stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(user_stmt).scalars().first()
        self._validate_property(user)

        type_stmt = select(DeviceType).filter_by(type='Garage Door')
        device_type = self.session.execute(type_stmt).scalars().first()

        device_id = str(uuid.uuid4())
        device = Devices(id=device_id, user_id=user.id, ip_address=ip_address, node_name=name, device_type_id=device_type.id)
        self.session.add(device)
        return device.id

    def get_user_garage_ip(self, user_id):
        stmt = select(Devices).where(Devices.user_id == user_id, Devices.device_type.has(DeviceType.type == 'Garage Door'))
        device = self.session.execute(stmt).scalars().first()
        self._validate_property(device)
        if device.ip_port is None:
            return device.ip_address
        return f'{device.ip_address}:{device.ip_port}'

    def __update_preference(self, node_name, node_size, user_id):
        stmt = select(UserPreference).filter_by(user_id=user_id)
        preference = self.session.execute(stmt).scalars().first()
        if preference is None:
            raise Unauthorized
        preference.garage_id = node_size + 1
        preference.garage_door = node_name