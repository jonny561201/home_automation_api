import uuid

from sqlalchemy import select, delete
from werkzeug.exceptions import BadRequest

from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import ChildAccounts, UserInformation, UserPreference


class AccountRepository(DatabaseBase):

    def get_user_child_accounts(self, user_id):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(parent_user_id=user_id)
        children = self.session.execute(stmt).scalars().all()
        if children is None:
            return []
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

    def delete_child_user_account(self, user_id, child_user_id):
        self._validate_property(user_id)
        child_stmt = delete(ChildAccounts).where(ChildAccounts.parent_user_id == user_id, ChildAccounts.child_user_id == child_user_id)
        self.session.execute(child_stmt)

    def create_child_account(self, user_id, email):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()
        if child_account is not None:
            raise BadRequest

        stmt = select(UserInformation).filter_by(id=user_id)
        parent = self.session.execute(stmt).scalars().first()
        self._validate_property(parent)

        new_user_id = str(uuid.uuid4())
        user_info = UserInformation(id=new_user_id, email=email, first_name=parent.first_name, last_name=parent.last_name)
        self.session.add(user_info)
        self.__create_user_preference(new_user_id, user_id)
        child = ChildAccounts(parent_user_id=user_id, child_user_id=new_user_id)
        self.session.add(child)
        return {'first_name': parent.first_name, 'last_name': parent.last_name, 'email': email, 'user_id': new_user_id}

    def insert_preferences_by_user(self, user_id, preference_info):
        if len(preference_info) == 0 or user_id is None:
            raise BadRequest
        city = preference_info.get('city')
        is_imperial = preference_info.get('isImperial')
        is_fahrenheit = preference_info.get('isFahrenheit')
        garage_door = preference_info.get('garageDoor')
        garage_id = preference_info.get('garageId', '')

        stmt = select(UserPreference).filter_by(user_id=user_id)
        record = self.session.execute(stmt).scalars().first()
        record.is_fahrenheit = is_fahrenheit if is_fahrenheit is not None else record.is_fahrenheit
        record.is_imperial = is_imperial if is_imperial is not None else record.is_imperial
        record.city = city if city is not None else record.city
        record.garage_door = garage_door if garage_door is not None else record.garage_door
        record.garage_id = garage_id if garage_id != '' else record.garage_id

    def provision_user(self, first_name, last_name, email):
        user_id = str(uuid.uuid4())
        user = UserInformation(id=user_id, first_name=first_name, last_name=last_name, email=email)
        self.session.add(user)
        return user_id

    def __get_user_info(self, user_id):
        stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(stmt).scalars().first()
        return {'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'user_id': str(user.id)}

    def __create_user_preference(self, new_user_id, user_id):
        stmt = select(UserPreference).filter_by(user_id=user_id)
        pref = self.session.execute(stmt).scalars().first()
        new_pref = UserPreference(user_id=new_user_id, is_fahrenheit=pref.is_fahrenheit, is_imperial=pref.is_imperial, city=pref.city)
        self.session.add(new_pref)

