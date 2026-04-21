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
        garage_node = preference.garage_node
        return Preference(city=preference.city,
                          state=preference.state,
                          garageAlertTime=preference.garage_alert_time,
                          measureUnit='imperial' if preference.is_imperial else 'metric',
                          garageId=str(preference.garage_node_id) if preference.garage_node_id else None,
                          garageName=garage_node.node_name if garage_node != None else None,
                          tempUnit='fahrenheit' if preference.is_fahrenheit else 'celsius')

    def insert_preferences_by_user(self, user_id, preference_info, garage_node_id=None):
        if len(preference_info) == 0 or user_id is None:
            raise BadRequest
        stmt = select(UserPreference).filter_by(user_id=user_id)
        record = self.session.execute(stmt).scalars().first()
        if record is None:
            record = UserPreference(user_id=user_id)
            self.session.add(record)
        record.is_fahrenheit = preference_info.get('isFahrenheit', True)
        record.is_imperial = preference_info.get('isImperial', True)
        record.city = preference_info.get('city', None)
        record.state = preference_info.get('state', None)
        record.garage_alert_time = preference_info.get('garageAlertTime', 0)
        record.garage_node_id = garage_node_id
