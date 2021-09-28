import uuid
from datetime import time, datetime, timedelta

import pytz
from sqlalchemy import orm, create_engine
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden

from svc.constants.settings_state import Settings
from svc.db.models.user_information_model import UserPreference, UserCredentials, DailySumpPumpLevel, \
    AverageSumpPumpLevel, RoleDevices, UserRoles, RoleDeviceNodes, ChildAccounts, UserInformation, ScheduleTasks, \
    ScheduledTaskTypes, Scenes, SceneDetails, RefreshToken


class UserDatabaseManager:
    db_session = None

    def __enter__(self):
        settings = Settings.get_instance()
        connection = f'postgresql://{settings.db_user}:{settings.db_pass}@localhost:{settings.db_port}/{settings.db_name}'

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
        return {'user_id': user.user_id,
                'roles': [self.__create_role(role.role_devices, role.role.role_name) for role in user.user_roles],
                'first_name': user.user.first_name,
                'last_name': user.user.last_name}

    def get_user_info(self, user_id):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        if user is None:
            raise Unauthorized
        return {'user_id': user.user_id,
                'roles': [self.__create_role(role.role_devices, role.role.role_name) for role in user.user_roles],
                'first_name': user.user.first_name,
                'last_name': user.user.last_name}

    def insert_refresh_token(self, refresh_token):
        token = RefreshToken()
        token.refresh = refresh_token
        token.count = 10
        token.expire_time = datetime.now(tz=pytz.timezone('US/Central')) + timedelta(hours=12)
        self.session.add(token)

    def generate_new_refresh_token(self, refresh_token):
        token = self.session.query(RefreshToken).filter_by(refresh=refresh_token).first()
        if token is None or token.expire_time < datetime.now(tz=pytz.timezone('US/Central')) or token.count <= 0:
            raise Forbidden
        new_refresh = str(uuid.uuid4())
        token.refresh = new_refresh
        token.expire_time = datetime.now(tz=pytz.timezone('US/Central')) + timedelta(hours=12)
        token.count -= 1
        return new_refresh

    def get_roles_by_user(self, user_id):
        self.__validate_property(user_id)
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        self.__validate_property(user)
        return {'roles': [self.__create_role(role.role_devices, role.role.role_name) for role in user.user_roles]}

    def change_user_password(self, user_id, old_pass, new_pass):
        self.__validate_property(user_id)
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        if user.password != old_pass:
            raise Unauthorized
        user.password = new_pass

    def get_preferences_by_user(self, user_id):
        self.__validate_property(user_id)
        preference = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        self.__validate_property(preference)
        return {'temp_unit': 'fahrenheit' if preference.is_fahrenheit else 'celsius',
                'measure_unit': 'imperial' if preference.is_imperial else 'metric',
                'city': preference.city,
                'is_fahrenheit': preference.is_fahrenheit,
                'is_imperial': preference.is_imperial}

    def insert_preferences_by_user(self, user_id, preference_info):
        if len(preference_info) == 0 or user_id is None:
            raise BadRequest
        city = preference_info.get('city')
        is_imperial = preference_info.get('isImperial')
        is_fahrenheit = preference_info.get('isFahrenheit')

        record = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        record.is_fahrenheit = is_fahrenheit if is_fahrenheit is not None else record.is_fahrenheit
        record.is_imperial = is_imperial if is_imperial is not None else record.is_imperial
        record.city = city if city is not None else record.city

    def update_schedule_task_by_user_id(self, user_id, task):
        self.__validate_property(user_id)
        old_task = self.session.query(ScheduleTasks).filter_by(user_id=user_id, id=task.get('taskId')).first()
        self.__validate_property(old_task)
        old_task.id = str(uuid.uuid4())
        old_task.alarm_days = task['alarmDays'] if task.get('alarmDays') else old_task.alarm_days
        old_task.alarm_time = time.fromisoformat(task['alarmTime']) if task.get('alarmTime') else old_task.alarm_time
        old_task.alarm_group_name = task['alarmGroupName'] if task.get('alarmGroupName') else old_task.alarm_group_name
        old_task.alarm_light_group = task['alarmLightGroup'] if task.get('alarmLightGroup') else old_task.alarm_light_group
        old_task.enabled = task['enabled'] if task.get('enabled') is not None else old_task.enabled
        old_task.hvac_start = time.fromisoformat(task['hvacStart']) if task.get('hvacStart') else old_task.hvac_start
        old_task.hvac_stop = time.fromisoformat(task['hvacStop']) if task.get('hvacStop') else old_task.hvac_stop
        old_task.hvac_mode = task['hvacMode'] if task.get('hvacMode') else old_task.hvac_mode
        old_task.hvac_start_temp = task['hvacStartTemp'] if task.get('hvacStartTemp') else old_task.hvac_start_temp
        old_task.hvac_stop_temp = task['hvacStopTemp'] if task.get('hvacStopTemp') else old_task.hvac_stop_temp

        if old_task.task_type.activity_name != task.get('taskType'):
            old_task.task_type = self.session.query(ScheduledTaskTypes).filter_by(activity_name=task.get('taskType')).first()
        return self.__create_scheduled_task(old_task)

    def delete_schedule_task_by_user(self, user_id, task_id):
        self.__validate_property(user_id)
        self.session.query(ScheduleTasks).filter_by(user_id=user_id, id=task_id).delete()

    def get_schedule_tasks_by_user(self, user_id, task_type):
        self.__validate_property(user_id)
        tasks = self.session.query(ScheduleTasks).filter_by(user_id=user_id).all()
        if task_type is not None:
            return [self.__create_scheduled_task(task) for task in tasks if task.task_type.activity_name == task_type.lower()]
        return [self.__create_scheduled_task(task) for task in tasks]

    def insert_schedule_task_by_user(self, user_id, task):
        self.__validate_property(user_id)
        try:
            alarm_time = None if task.get('alarmTime') is None else time.fromisoformat(task.get('alarmTime'))
            hvac_start = None if task.get('hvacStart') is None else time.fromisoformat(task.get('hvacStart'))
            hvac_stop = None if task.get('hvacStop') is None else time.fromisoformat(task.get('hvacStop'))
            task_type = self.session.query(ScheduledTaskTypes).filter_by(activity_name=task.get('taskType')).first()
            new_task = ScheduleTasks(user_id=user_id, alarm_light_group=task.get('alarmLightGroup'), alarm_days=task['alarmDays'],
                                     alarm_group_name=task.get('alarmGroupName'), alarm_time=alarm_time, task_type=task_type, enabled=task['enabled'],
                                     hvac_mode=task.get('hvacMode'), hvac_start=hvac_start, hvac_stop=hvac_stop,
                                     hvac_start_temp=task.get('hvacStartTemp'), hvac_stop_temp=task.get('hvacStopTemp'))
            self.session.add(new_task)
        except KeyError:
            raise BadRequest
        new_tasks = self.session.query(ScheduleTasks).filter_by(user_id=user_id).all()
        return [self.__create_scheduled_task(task) for task in new_tasks]

    def get_current_sump_level_by_user(self, user_id):
        self.__validate_property(user_id)
        child_account = self.session.query(ChildAccounts).filter_by(child_user_id=user_id).first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id
        sump_level = self.session.query(DailySumpPumpLevel).filter_by(user_id=select_user_id).order_by(DailySumpPumpLevel.id.desc()).first()
        self.__validate_property(sump_level)
        return {'currentDepth': float(sump_level.distance), 'warningLevel': sump_level.warning_level}

    def get_average_sump_level_by_user(self, user_id):
        self.__validate_property(user_id)
        child_account = self.session.query(ChildAccounts).filter_by(child_user_id=user_id).first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id
        average = self.session.query(AverageSumpPumpLevel).filter_by(user_id=select_user_id).order_by(AverageSumpPumpLevel.id.desc()).first()
        self.__validate_property(average)
        return {'latestDate': str(average.create_day), 'averageDepth': float(average.distance)}

    def insert_current_sump_level(self, user_id, depth_info):
        self.__validate_property(user_id)
        try:
            depth = depth_info['depth']
            date = depth_info['datetime']
            warning_level = depth_info['warning_level']
            current_depth = DailySumpPumpLevel(distance=depth, create_date=date, warning_level=warning_level, user_id=user_id)

            self.session.add(current_depth)
        except (TypeError, KeyError):
            raise BadRequest

    def add_new_role_device(self, user_id, role_name, ip_address):
        self.__validate_property(user_id)
        child_account = self.session.query(ChildAccounts).filter_by(child_user_id=user_id).first()
        select_user_id = user_id if child_account is None else child_account.parent_user_id
        user_roles = self.session.query(UserRoles).filter_by(user_id=select_user_id).all()
        role = next((user_role for user_role in user_roles if user_role.role.role_name == role_name), None)
        if role is None:
            raise Unauthorized
        device_id = uuid.uuid4()
        device = RoleDevices(id=str(device_id), ip_address=ip_address, max_nodes=2, user_role_id=role.id)
        self.session.add(device)
        return str(device_id)

    # TODO: should validate user_id matches result from db else 401
    def add_new_device_node(self, user_id, device_id, node_name):
        self.__validate_property(user_id)
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
        self.__validate_property(user_id)
        user_role = self.session.query(UserRoles).filter_by(user_id=user_id).first()
        self.__validate_property(user_role)
        return user_role.role_devices.ip_address

    def get_user_child_accounts(self, user_id):
        self.__validate_property(user_id)
        children = self.session.query(ChildAccounts).filter_by(parent_user_id=user_id).all()
        if children is None:
            return []
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

    def delete_child_user_account(self, user_id, child_user_id):
        self.__validate_property(user_id)
        self.session.query(ChildAccounts).filter_by(parent_user_id=user_id, child_user_id=child_user_id).delete()
        self.session.query(UserCredentials).filter_by(user_id=child_user_id).delete()

    def create_child_account(self, user_id, email, roles, new_pass):
        self.__validate_property(user_id)
        child_account = self.session.query(ChildAccounts).filter_by(child_user_id=user_id).first()
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
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
        self.session.commit()
        children = self.session.query(ChildAccounts).filter_by(parent_user_id=user_id).all()
        children_ids = [child.child_user_id for child in children]
        return [self.__get_user_info(child_id) for child_id in children_ids]

    def get_scenes_by_user(self, user_id):
        self.__validate_property(user_id)
        scenes = self.session.query(Scenes).filter_by(user_id=user_id).all()
        if scenes is None:
            return []
        return [{'name': scene.name, 'lights': self.__create_light_scenes(scene.details)} for scene in scenes]

    def delete_scene_by_user(self, user_id, scene_id):
        self.__validate_property(user_id)
        self.__validate_property(scene_id)
        self.session.query(SceneDetails).filter_by(scene_id=scene_id).delete()
        self.session.query(Scenes).filter_by(user_id=user_id, id=scene_id).delete()

    @staticmethod
    def __create_light_scenes(light_details):
        return [{'group_name': detail.light_group_name, 'group_id': detail.light_group, 'brightness': detail.light_brightness} for detail in light_details]

    def __duplicate_roles(self, new_user_id, user_role):
        role_id = str(uuid.uuid4())
        new_user_role = UserRoles(user_id=new_user_id, role_id=user_role.role_id, id=role_id)
        new_user_role.role = user_role.role
        self.session.add(new_user_role)
        self.session.commit()
        if user_role.role_devices is not None:
            device_id = str(uuid.uuid4())
            self.session.add(RoleDevices(id=device_id, ip_address=user_role.role_devices.ip_address, max_nodes=user_role.role_devices.max_nodes, user_role_id=role_id))
            self.session.commit()
            if user_role.role_devices.role_device_nodes:
                for node_device in user_role.role_devices.role_device_nodes:
                    self.session.add(RoleDeviceNodes(role_device_id=device_id, node_name=node_device.node_name, node_device=node_device.node_device))

    def __get_user_info(self, user_id):
        user = self.session.query(UserCredentials).filter_by(user_id=user_id).first()
        return {'user_name': user.user_name, 'user_id': user_id,
                'roles': [role.role.role_name for role in user.user_roles]}

    def __create_user_preference(self, new_user_id, user_id):
        pref = self.session.query(UserPreference).filter_by(user_id=user_id).first()
        new_pref = UserPreference(user_id=new_user_id, is_fahrenheit=pref.is_fahrenheit, is_imperial=pref.is_imperial, city=pref.city)
        self.session.add(new_pref)

    @staticmethod
    def __validate_property(record):
        if record is None:
            raise BadRequest()

    @staticmethod
    def __create_scheduled_task(task):
        alarm_time = None if task.alarm_time is None else task.alarm_time.isoformat()
        hvac_start = None if task.hvac_start is None else task.hvac_start.isoformat()
        hvac_stop = None if task.hvac_stop is None else task.hvac_stop.isoformat()
        return {'alarm_group_name': task.alarm_group_name, 'alarm_light_group': task.alarm_light_group, 'task_id': str(task.id), 'enabled': task.enabled,
                'alarm_days': task.alarm_days, 'alarm_time': alarm_time, 'task_type': task.task_type.activity_name, 'hvac_mode': task.hvac_mode,
                'hvac_start': hvac_start, 'hvac_stop': hvac_stop, 'hvac_start_temp': task.hvac_start_temp, 'hvac_stop_temp': task.hvac_stop_temp}

    @staticmethod
    def __create_role(role_devices, role_name):
        if role_devices is not None:
            return {'ip_address': role_devices.ip_address, 'role_name': role_name, 'device_id': role_devices.id,
                    'devices': [{'node_device': node.node_device, 'node_name': node.node_name} for node in role_devices.role_device_nodes]}
        else:
            return {'role_name': role_name}
