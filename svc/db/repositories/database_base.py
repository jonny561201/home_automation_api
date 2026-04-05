from sqlalchemy import create_engine, orm, select
from werkzeug.exceptions import NotFound

from svc.config.settings_state import Settings
from svc.db.models.user_information_model import UserPreference
from svc.models.app import Preference


class DatabaseBase:
    _engine = None
    _scoped_session = None

    def __init__(self):
        if DatabaseBase._engine is None:
            settings = Settings.get_instance().Database
            connection = f'postgresql://{settings.user}:{settings.password}@localhost:{settings.port}/{settings.name}'
            DatabaseBase._engine = create_engine(connection)
            DatabaseBase._scoped_session = orm.scoped_session(orm.sessionmaker(bind=DatabaseBase._engine))
        self.session = None

    def __enter__(self):
        self.session = DatabaseBase._scoped_session
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.commit()
        self.session.remove()

    def get_preferences_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(UserPreference).filter_by(user_id=user_id)
        preference = self.session.execute(stmt).scalars().first()
        self._validate_property(preference)
        return Preference(isFahrenheit=preference.is_fahrenheit, isImperial=preference.is_imperial, city=preference.city,
                          measureUnit='imperial' if preference.is_imperial else 'metric',
                          garageDoor=preference.garage_door, garageId=preference.garage_id,
                          tempUnit='fahrenheit' if preference.is_fahrenheit else 'celsius')

    @staticmethod
    def _validate_property(record):
        if record is None:
            raise NotFound()
