import uuid

from sqlalchemy import select, delete
from werkzeug.exceptions import BadRequest

from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import ChildAccounts, UserCredentials, UserInformation, UserPreference, \
    UserRoles, Devices, RoleDeviceNodes


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
        user_stmt = delete(UserCredentials).where(UserCredentials.user_id == child_user_id)
        self.session.execute(user_stmt)

    def create_child_account(self, user_id, email, roles, new_pass):
        self._validate_property(user_id)
        stmt = select(ChildAccounts).filter_by(child_user_id=user_id)
        child_account = self.session.execute(stmt).scalars().first()

        stmt = select(UserCredentials).filter_by(user_id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user is None or child_account is not None:
            raise BadRequest

        new_user_id = str(uuid.uuid4())
        user_info = UserInformation(id=new_user_id, email=email, first_name=user.user.first_name, last_name=user.user.last_name)
        user_creds = UserCredentials(id=str(uuid.uuid4()), user_name=email, password=new_pass, user_id=new_user_id)
        self.session.add(user_info)
        self.session.add(user_creds)

        for user_role in user.user_roles:
            if user_role.role.role_name in roles:
                self.__duplicate_roles(new_user_id, user_role)

        self.__create_user_preference(new_user_id, user_id)
        child = ChildAccounts(parent_user_id=user_id, child_user_id=new_user_id)
        self.session.add(child)
        stmt = select(ChildAccounts).filter_by(parent_user_id=user_id)
        children = self.session.execute(stmt).scalars().all()
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

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
        stmt = select(UserCredentials).filter_by(user_id=user_id)
        user = self.session.execute(stmt).scalars().first()
        return {'user_name': user.user_name, 'user_id': str(user_id),
                'roles': [role.role.role_name for role in user.user_roles]}

    def __create_user_preference(self, new_user_id, user_id):
        stmt = select(UserPreference).filter_by(user_id=user_id)
        pref = self.session.execute(stmt).scalars().first()
        new_pref = UserPreference(user_id=new_user_id, is_fahrenheit=pref.is_fahrenheit, is_imperial=pref.is_imperial, city=pref.city)
        self.session.add(new_pref)

    def __duplicate_roles(self, new_user_id, user_role):
        role_id = str(uuid.uuid4())
        new_user_role = UserRoles(user_id=new_user_id, role_id=user_role.role_id, id=role_id)
        new_user_role.role = user_role.role
        self.session.add(new_user_role)
        if user_role.role_devices is not None:
            device_id = str(uuid.uuid4())
            self.session.add(Devices(id=device_id, ip_address=user_role.role_devices.ip_address, max_nodes=user_role.role_devices.max_nodes, user_role_id=role_id))
            if user_role.role_devices.role_device_nodes:
                for node_device in user_role.role_devices.role_device_nodes:
                    self.session.add(RoleDeviceNodes(role_device_id=device_id, node_name=node_device.node_name, node_device=node_device.node_device))
