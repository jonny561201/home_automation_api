from sqlalchemy import create_engine, orm
from werkzeug.exceptions import NotFound

from svc.config.settings_state import Settings


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

    @staticmethod
    def _validate_property(record):
        if record is None:
            raise NotFound()
