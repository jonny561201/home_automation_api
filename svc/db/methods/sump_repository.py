from sqlalchemy import select
from werkzeug.exceptions import BadRequest

from svc.db.methods.database_base import DatabaseBase
from svc.db.models.user_information_model import ChildAccounts, DailySumpPumpLevel, AverageSumpPumpLevel


class SumpDatabase(DatabaseBase):

    def get_current_sump_level_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id

        stmt = select(DailySumpPumpLevel).where(DailySumpPumpLevel.user_id == select_user_id).order_by(DailySumpPumpLevel.id.desc())
        sump_level = self.session.execute(stmt).scalars().first()
        self._validate_property(sump_level)
        return {'currentDepth': float(sump_level.distance), 'warningLevel': sump_level.warning_level}

    def get_average_sump_level_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id

        stmt = select(AverageSumpPumpLevel).where(AverageSumpPumpLevel.user_id == select_user_id).order_by(AverageSumpPumpLevel.id.desc())
        average = self.session.execute(stmt).scalars().first()
        self._validate_property(average)
        return {'latestDate': average.create_day, 'averageDepth': float(average.distance)}

    def insert_current_sump_level(self, user_id, depth_info):
        self._validate_property(user_id)
        try:
            depth = depth_info['depth']
            date = depth_info['datetime']
            warning_level = depth_info['warning_level']
            current_depth = DailySumpPumpLevel(distance=depth, create_date=date, warning_level=warning_level, user_id=user_id)

            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise BadRequest
