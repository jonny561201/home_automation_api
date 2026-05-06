from sqlalchemy import select
from werkzeug.exceptions import Unauthorized, BadRequest

from svc.models.app import Preference
from svc.db.models.user_information_model import UserInformation, UserPreference
from svc.db.repositories.database_base import DatabaseBase


class UserRepository(DatabaseBase):

    def get_user_info(self, user_id):
        stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user is None:
            raise Unauthorized
        return {'user_id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name}

    def get_preferences_by_user(self, user_id):
        self._validate_property(user_id)
        stmt = select(UserPreference).filter_by(user_id=user_id)
        preference = self.session.execute(stmt).scalars().first()
        self._validate_property(preference)
        return Preference(city=preference.city,
                          state=preference.state,
                          latitude=float(preference.latitude) if preference.latitude is not None else None,
                          longitude=float(preference.longitude) if preference.longitude is not None else None,
                          garageAlertTime=preference.garage_alert_time,
                          measureUnit='imperial' if preference.is_imperial else 'metric',
                          garageNodeId=str(preference.garage_node_id) if preference.garage_node_id else None,
                          tempUnit='fahrenheit' if preference.is_fahrenheit else 'celsius')

    def insert_preferences_by_user(self, user_id, preference_info, garage_node_id=None):
        if user_id is None:
            raise BadRequest()
        stmt = select(UserPreference).filter_by(user_id=user_id)
        record = self.session.execute(stmt).scalars().first()
        if record is None:
            record = UserPreference(user_id=user_id, is_fahrenheit=True, is_imperial=True, garage_alert_time=0)
            self.session.add(record)
        if 'isFahrenheit' in preference_info:
            record.is_fahrenheit = preference_info['isFahrenheit']
        if 'isImperial' in preference_info:
            record.is_imperial = preference_info['isImperial']
        if 'city' in preference_info:
            record.city = preference_info['city']
        if 'state' in preference_info:
            record.state = preference_info['state']
        if 'latitude' in preference_info:
            record.latitude = preference_info['latitude']
        if 'longitude' in preference_info:
            record.longitude = preference_info['longitude']
        if 'garageAlertTime' in preference_info:
            record.garage_alert_time = preference_info['garageAlertTime']
        if garage_node_id is not None:
            record.garage_node_id = garage_node_id
