import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DECIMAL, TIMESTAMP, DATE
from sqlalchemy.dialects.postgresql import UUID, INET, SMALLINT, TIME
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship

Base = declarative.declarative_base()


class RefreshToken(Base):
    __tablename__ = 'refresh_token'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    refresh = Column(UUID, nullable=False)
    count = Column(SMALLINT, nullable=False)


class UserInformation(Base):
    __tablename__ = 'user_information'

    id = Column(UUID, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    child_accounts = relationship("ChildAccounts", cascade='delete', primaryjoin="and_(ChildAccounts.parent_user_id == UserInformation.id)", viewonly=True)


class ChildAccounts(Base):
    __tablename__ = 'child_accounts'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    child_user_id = Column(UUID, ForeignKey(UserInformation.id))
    parent_user_id = Column(UUID, ForeignKey(UserInformation.id))


class Roles(Base):
    __tablename__ = 'roles'

    id = Column(UUID, nullable=False, primary_key=True)
    role_desc = Column(String, nullable=False)
    role_name = Column(String, nullable=False)


class UserRoles(Base):
    __tablename__ = 'user_roles'

    id = Column(UUID, nullable=False, primary_key=True)
    role_id = Column(UUID, ForeignKey(Roles.id))
    user_id = Column(UUID, ForeignKey(UserInformation.id))

    role = relationship('Roles', foreign_keys='UserRoles.role_id')
    role_devices = relationship("RoleDevices", cascade='delete', backref="parent", uselist=False, lazy='joined')


class RoleDevices(Base):
    __tablename__ = 'role_devices'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    ip_address = Column(INET, nullable=False)
    max_nodes = Column(SMALLINT, nullable=False)
    user_role_id = Column(UUID, ForeignKey(UserRoles.id))

    role_device_nodes = relationship("RoleDeviceNodes", cascade='delete', backref="parent", lazy='joined')


class RoleDeviceNodes(Base):
    __tablename__ = 'role_device_nodes'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    node_name = Column(String, nullable=False)
    node_device = Column(SMALLINT, nullable=True)
    role_device_id = Column(UUID, ForeignKey(RoleDevices.id))


class Scenes(Base):
    __tablename__ = 'scenes'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey(UserInformation.id))

    details = relationship('SceneDetails', cascade='delete', backref="parent", lazy='joined')


class SceneDetails(Base):
    __tablename__ = 'scene_details'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    scene_id = Column(UUID, ForeignKey(Scenes.id))
    light_group = Column(String, nullable=True)
    light_group_name = Column(String, nullable=True)
    light_brightness = Column(SMALLINT, nullable=True)


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    is_fahrenheit = Column(Boolean, nullable=False)
    is_imperial = Column(Boolean, nullable=False)
    city = Column(String, nullable=True)

    user = relationship('UserInformation', foreign_keys='UserPreference.user_id')


class ScheduledTaskTypes(Base):
    __tablename__ = 'scheduled_task_types'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    activity_name = Column(String, nullable=False)
    activity_desc = Column(String, nullable=False)


class ScheduleTasks(Base):
    __tablename__ = 'schedule_tasks'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    alarm_time = Column(TIME, nullable=True)
    alarm_days = Column(String, nullable=True)
    alarm_light_group = Column(String, nullable=True)
    alarm_group_name = Column(String, nullable=True)
    hvac_start = Column(TIME, nullable=True)
    hvac_stop = Column(TIME, nullable=True)
    hvac_mode = Column(String, nullable=True)
    hvac_start_temp = Column(Integer, nullable=True)
    hvac_stop_temp = Column(Integer, nullable=True)
    enabled = Column(Boolean, nullable=False)
    task_type_id = Column(UUID, ForeignKey(ScheduledTaskTypes.id))

    user = relationship('UserInformation', foreign_keys='ScheduleTasks.user_id')
    task_type = relationship('ScheduledTaskTypes', foreign_keys='ScheduleTasks.task_type_id')


# TODO: remove cascade delete on user roles
class UserCredentials(Base):
    __tablename__ = 'user_login'

    id = Column(UUID, nullable=False, primary_key=True)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey(UserInformation.id))

    user = relationship('UserInformation', cascade='delete', foreign_keys='UserCredentials.user_id')
    user_roles = relationship("UserRoles", cascade='delete', secondaryjoin="and_(UserRoles.user_id == UserInformation.id)", secondary='user_information', viewonly=True)


class DailySumpPumpLevel(Base):
    __tablename__ = 'daily_sump_level'

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    distance = Column(DECIMAL, nullable=False)
    warning_level = Column(Integer, nullable=False)
    create_date = Column(TIMESTAMP, nullable=False)

    user = relationship('UserInformation', foreign_keys='DailySumpPumpLevel.user_id')


class AverageSumpPumpLevel(Base):
    __tablename__ = 'average_daily_sump_level'

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    distance = Column(DECIMAL, nullable=False)
    create_day = Column(DATE, nullable=False)

    user = relationship('UserInformation', foreign_keys='AverageSumpPumpLevel.user_id')
