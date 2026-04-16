from sqlalchemy import select
from werkzeug.exceptions import NotFound

from svc.db.models.user_information_model import ChildAccounts, DailySumpPumpLevel, AverageSumpPumpLevel, Devices, DeviceType
from svc.db.repositories.database_base import DatabaseBase


class SumpRepository(DatabaseBase):

    def get_sump_device_id_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()
        resolved_user_id = user_id if child_account is None else child_account.parent_user_id

        stmt = select(Devices).where(
            Devices.user_id == resolved_user_id,
            Devices.device_type.has(DeviceType.type == 'sump_pump')
        )
        device = self.session.execute(stmt).scalars().first()
        self._validate_property(device)
        return str(device.id)

    def get_current_sump_level_by_device(self, device_id):
        self._validate_property(device_id)
        stmt = select(DailySumpPumpLevel).where(DailySumpPumpLevel.device_id == device_id).order_by(DailySumpPumpLevel.id.desc())
        sump_level = self.session.execute(stmt).scalars().first()
        self._validate_property(sump_level)
        return sump_level

    def get_average_sump_level_by_device(self, device_id):
        self._validate_property(device_id)
        stmt = select(AverageSumpPumpLevel).where(AverageSumpPumpLevel.device_id == device_id).order_by(AverageSumpPumpLevel.id.desc())
        average = self.session.execute(stmt).scalars().first()
        self._validate_property(average)
        return average

    def insert_current_sump_level(self, device_id, depth_info):
        self._validate_property(device_id)
        try:
            depth = depth_info['depth']
            date = depth_info['datetime']
            warning_level = depth_info['warning_level']
            current_depth = DailySumpPumpLevel(distance=depth, create_date=date, warning_level=warning_level, device_id=device_id)

            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise NotFound
