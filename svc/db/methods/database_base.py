from sqlalchemy import create_engine, orm, select
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import UserPreference
from svc.models.app import Preference
from svc.config.settings_state import Settings


class DatabaseBase:
    def __init__(self):
        self.session = None

    def __enter__(self):
        settings = Settings.get_instance().Database
        connection = f'postgresql://{settings.user}:{settings.password}@localhost:{settings.port}/{settings.name}'

        db_engine = create_engine(connection)
        session = orm.sessionmaker(bind=db_engine)
        self.session = orm.scoped_session(session)

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
    def _create_role(role_devices, role_name):
        if role_devices is not None:
            return {'ip_address': role_devices.ip_address, 'role_name': role_name,
                    'device_id': str(role_devices.id),
                    'devices': [{'node_device': node.node_device, 'node_name': node.node_name} for node in
                                role_devices.role_device_nodes]}
        else:
            return {'role_name': role_name}

    #TODO: maybe throw different error?  mostly used when no user_id found
    @staticmethod
    def _validate_property(record):
        if record is None:
            raise BadRequest()
