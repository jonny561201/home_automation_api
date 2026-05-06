from datetime import date, timedelta

from sqlalchemy import select, func
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
        return self.session.execute(stmt).scalars().first()

    def get_daily_readings_by_device(self, device_id):
        self._validate_property(device_id)
        today = date.today()
        stmt = (select(DailySumpPumpLevel).where(DailySumpPumpLevel.device_id == device_id, func.date(DailySumpPumpLevel.create_date) == today)
                .order_by(DailySumpPumpLevel.create_date.asc()))
        return self.session.execute(stmt).scalars().all()

    def get_average_readings_by_device(self, device_id, days):
        self._validate_property(device_id)
        start_date = date.today() - timedelta(days=days)
        stmt = (select(AverageSumpPumpLevel).where(AverageSumpPumpLevel.device_id == device_id, AverageSumpPumpLevel.create_day >= start_date)
                .order_by(AverageSumpPumpLevel.create_day.asc()))
        return self.session.execute(stmt).scalars().all()

    def insert_current_sump_level(self, device_id, depth_info):
        self._validate_property(device_id)
        try:
            current_depth = DailySumpPumpLevel(distance=depth_info['depth'], create_date=depth_info['datetime'], warning_level=depth_info['alert_level'], device_id=device_id)
            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise NotFound

    def insert_average_sump_level(self, device_id, depth_info):
        self._validate_property(device_id)
        try:
            average_depth = AverageSumpPumpLevel(distance=depth_info['depth'], device_id=device_id, create_day=depth_info['date'])
            self.session.add(average_depth)
        except (TypeError, KeyError):
            raise NotFound
