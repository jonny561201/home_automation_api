import uuid

from sqlalchemy import orm, create_engine
from sqlalchemy.orm import make_transient
from werkzeug.exceptions import BadRequest, Unauthorized

from svc.constants.settings_state import Settings
from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel, RoleDevices, UserRoles, RoleDeviceNodes, ChildAccounts


class UserDatabaseManager:
    db_session = None

    def __enter__(self):
        settings = Settings.get_instance()
        connection = 'postgresql://%s:%s@localhost:%s/%s' % (settings.db_user, settings.db_pass, settings.db_port, settings.db_name)

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

    def validate_credentials(self, user_name, pword):
        user = self.session.query(UserCredentials).filter_by(user_name=user_name).first()
        if user is None or user.password != pword:
            raise Unauthorized
        return {'user_id': user.user_id, 'roles': [self.__create_role(role.role_devices, role.role.role_name) for role in user.user_roles],
                'first_name': user.user.first_name, 'last_name': user.user.last_name}

    def get_roles_by_user(self, user_id):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        if user is None:
            raise BadRequest
        return {'roles': [self.__create_role(role.role_devices, role.role.role_name) for role in user.user_roles]}

    def change_user_password(self, user_id, old_pass, new_pass):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        if user.password != old_pass:
            raise Unauthorized
        user.password = new_pass

    def get_preferences_by_user(self, user_id):
        preference = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        if preference is None:
            raise BadRequest
        light_info = {'alarm_light_group': preference.alarm_light_group,
                      'alarm_time': preference.alarm_time,
                      'alarm_days': preference.alarm_days,
                      'alarm_group_name': preference.alarm_group_name}
        return {'temp_unit': 'fahrenheit' if preference.is_fahrenheit else 'celsius',
                'measure_unit': 'imperial' if preference.is_imperial else 'metric',
                'city': preference.city,
                'is_fahrenheit': preference.is_fahrenheit,
                'is_imperial': preference.is_imperial,
                'light_alarm': light_info}

    def insert_preferences_by_user(self, user_id, preference_info):
        city = preference_info.get('city')
        light_alarm = preference_info.get('lightAlarm')
        is_imperial = preference_info.get('isImperial')
        is_fahrenheit = preference_info.get('isFahrenheit')
        if len(preference_info) == 0:
            raise BadRequest

        record = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        record.is_fahrenheit = is_fahrenheit if is_fahrenheit is not None else record.is_fahrenheit
        record.is_imperial = is_imperial if is_imperial is not None else record.is_imperial
        record.city = city if city is not None else record.city
        record.alarm_days = light_alarm.get('alarmDays') if light_alarm is not None else record.alarm_days
        record.alarm_time = light_alarm.get('alarmTime') if light_alarm is not None else record.alarm_time
        record.alarm_light_group = light_alarm.get('alarmLightGroup') if light_alarm is not None else record.alarm_light_group
        record.alarm_group_name = light_alarm.get('alarmGroupName') if light_alarm is not None else record.alarm_group_name

    def get_current_sump_level_by_user(self, user_id):
        sump_level = self.session.query(DailySumpPumpLevel).filter_by(user_id=user_id).order_by(DailySumpPumpLevel.id.desc()).first()
        if sump_level is None:
            raise BadRequest
        return {'currentDepth': float(sump_level.distance), 'warningLevel': sump_level.warning_level}

    def get_average_sump_level_by_user(self, user_id):
        average = self.session.query(AverageSumpPumpLevel).filter_by(user_id=user_id).order_by(AverageSumpPumpLevel.id.desc()).first()
        if average is None:
            raise BadRequest
        return {'latestDate': str(average.create_day), 'averageDepth': float(average.distance)}

    def insert_current_sump_level(self, user_id, depth_info):
        try:
            depth = depth_info['depth']
            date = depth_info['datetime']
            warning_level = depth_info['warning_level']
            current_depth = DailySumpPumpLevel(distance=depth, create_date=date, warning_level=warning_level, user_id=user_id)

            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise BadRequest

    def add_new_role_device(self, user_id, role_name, ip_address):
        user_roles = self.session.query(UserRoles).filter_by(user_id=user_id).all()
        role = next((user_role for user_role in user_roles if user_role.role.role_name == role_name), None)
        if role is None:
            raise Unauthorized
        device_id = uuid.uuid4()
        device = RoleDevices(id=str(device_id), ip_address=ip_address, max_nodes=2, user_role_id=role.id)
        self.session.add(device)
        return str(device_id)

    # TODO: should validate user_id matches else 401
    def add_new_device_node(self, user_id, device_id, node_name):
        device = self.session.query(RoleDevices).filter_by(id=device_id).first()
        if device is None:
            raise Unauthorized
        node_size = len(device.role_device_nodes)
        if node_size >= device.max_nodes:
            raise BadRequest
        node = RoleDeviceNodes(node_name=node_name, role_device_id=device_id, node_device=node_size + 1)
        self.session.add(node)
        return {'availableNodes': device.max_nodes - (node_size + 1)}

    def get_user_garage_ip(self, user_id):
        user_role = self.session.query(UserRoles).filter_by(user_id=user_id).first()
        if user_role is None:
            raise BadRequest
        return user_role.role_devices.ip_address

    def get_user_child_accounts(self, user_id):
        children = self.session.query(ChildAccounts).filter_by(parent_user_id=user_id).all()
        if children is None:
            return []
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

    #TODO: just create a new account if the parent user exists
    def create_child_account(self, user_id, email, roles, new_pass):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        if user is None:
            raise BadRequest

        new_user_id = str(uuid.uuid4())
        for user_role in user.user_roles:
            if user_role.role.role_name in roles:
                self.__detach_relationship(user_role)
                user_role.user_id = new_user_id
                user_role.id = str(uuid.uuid4())
        self.__detach_relationship(user.user)
        self.__detach_relationship(user)
        self.__update_user(new_user_id, user, email, new_pass)
        child = ChildAccounts(parent_user_id=user_id, child_user_id=new_user_id)

        self.session.add(user.user)
        self.session.commit()
        self.session.add(user)
        [self.session.add(role) for role in user.user_roles]
        self.session.add(child)
        self.session.commit()
        children = self.session.query(ChildAccounts).filter_by(parent_user_id=user_id).all()
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

    def delete_child_user_account(self, user_id, child_user_id):
        self.session.query(ChildAccounts).filter_by(parent_user_id=user_id, child_user_id=child_user_id).delete()
        self.session.query(UserCredentials).filter_by(user_id=child_user_id).delete()

    def __detach_relationship(self, model):
        self.session.expunge(model)
        make_transient(model)

    def __get_user_info(self, user_id):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        return {'user_name': user.user_name, 'user_id': user_id, 'roles': [role.role.role_name for role in user.user_roles]}

    @staticmethod
    def __update_user(updated_user_id, user, email, new_pass):
        user.user_id = updated_user_id
        user.id = str(uuid.uuid4())
        user.user.id = updated_user_id
        user.user.email = email
        user.user_name = email
        user.password = new_pass

    @staticmethod
    def __create_role(role_devices, role_name):
        if role_devices is not None:
            return {'ip_address': role_devices.ip_address, 'role_name': role_name, 'device_id': role_devices.id,
                    'devices': [{'node_device': node.node_device, 'node_name': node.node_name} for node in role_devices.role_device_nodes]}
        else:
            return {'role_name': role_name}
