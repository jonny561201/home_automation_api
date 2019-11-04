from sqlalchemy import orm, create_engine
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel


class UserDatabaseManager:
    db_session = None

    def __enter__(self):
        connection = 'postgres://postgres:password@localhost:5432/garage_door'

        db_engine = create_engine(connection)
        session = orm.sessionmaker(bind=db_engine)
        self.db_session = orm.scoped_session(session)

        return UserDatabase(self.db_session)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db_session.commit()
        self.db_session.remove()


class UserDatabase:
    def __init__(self, session):
        self.session = session

    def validate_credentials(self, user, pword):
        user = self.session.query(UserCredentials).filter_by(user_name=user).first()
        if user is None or user.password != pword:
            raise Unauthorized
        return user.user_id

    def get_preferences_by_user(self, user_id):
        preference = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        if preference is None:
            raise BadRequest
        return preference

    def get_current_sump_level_by_user(self, user_id):
        sump_level = self.session.query(DailySumpPumpLevel).filter_by(user_id=user_id).order_by(DailySumpPumpLevel.id.desc()).first()
        if sump_level is None:
            raise BadRequest
        return float(sump_level.distance)

    def get_average_sump_level_by_user(self, user_id):
        average = self.session.query(AverageSumpPumpLevel).filter_by(user_id=user_id).order_by(AverageSumpPumpLevel.id.desc()).first()
        if average is None:
            raise BadRequest
        return {'latestDate': str(average.create_day), 'averageDepth': float(average.distance)}

# TODO: add new column alert_level
    def insert_current_sump_level(self, user_id, depth_info):
        try:
            depth = depth_info['depth']
            date = depth_info['datetime']
            warning_level = depth_info['warning_level']
            current_depth = DailySumpPumpLevel(distance=depth, create_date=date, warning_level=warning_level, user_id=user_id)

            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise BadRequest
