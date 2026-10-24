from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from svc.db.models.user_information_model import DeviceAlertState
from svc.db.repositories.database_base import DatabaseBase


class DeviceAlertStateRepository(DatabaseBase):

    def get_last_notified(self, device_id, alert_key):
        stmt = select(DeviceAlertState).where(
            DeviceAlertState.device_id == device_id,
            DeviceAlertState.alert_key == alert_key
        )
        record = self.session.execute(stmt).scalars().first()
        return record.last_notified if record != None else None

    def upsert_last_notified(self, device_id, alert_key, last_notified):
        stmt = insert(DeviceAlertState).values(device_id=device_id, alert_key=alert_key, last_notified=last_notified)
        stmt = stmt.on_conflict_do_update(index_elements=['device_id', 'alert_key'], set_={'last_notified': last_notified})
        self.session.execute(stmt)
