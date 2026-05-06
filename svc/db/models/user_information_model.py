import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DECIMAL, TIMESTAMP, DATE
from sqlalchemy.dialects.postgresql import UUID, INET, SMALLINT, TIME
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserInformation(Base):
    __tablename__ = 'user_information'

    id = Column(UUID, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)

    child_accounts = relationship("ChildAccounts", primaryjoin="and_(ChildAccounts.parent_user_id == UserInformation.id)", viewonly=True)


class ChildAccounts(Base):
    __tablename__ = 'child_accounts'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    child_user_id = Column(UUID, ForeignKey(UserInformation.id))
    parent_user_id = Column(UUID, ForeignKey(UserInformation.id))


class DeviceType(Base):
    __tablename__ = 'device_type'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    type = Column(String, nullable=False)
    auth0_role_id = Column(String, nullable=True)

class Devices(Base):
    __tablename__ = 'devices'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    ip_address = Column(INET, nullable=False)
    ip_port = Column(Integer)
    api_key = Column(String, nullable=False)
    name = Column(String, nullable=False)
    max_nodes = Column(SMALLINT, nullable=False, default=1)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    device_type_id = Column(UUID, ForeignKey(DeviceType.id))
    registered = Column(Boolean, nullable=False, default=False)

    device_type = relationship('DeviceType', foreign_keys='Devices.device_type_id')
    nodes = relationship('DeviceNodes', back_populates='device', cascade='all, delete-orphan')


class DeviceNodes(Base):
    __tablename__ = 'device_nodes'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    device_id = Column(UUID, ForeignKey(Devices.id), nullable=False)
    node_device = Column(SMALLINT, nullable=False)
    node_name = Column(String, nullable=False)

    device = relationship('Devices', back_populates='nodes')


class UserDevices(Base):
    __tablename__ = 'user_devices'

    id = Column(UUID, nullable=False, primary_key=True, server_default=sqlalchemy.text("gen_random_uuid()"))
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    device_id = Column(UUID, ForeignKey(Devices.id))

    device = relationship('Devices', foreign_keys='UserDevices.device_id')


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
    light_id = Column(String, nullable=True)
    light_brightness = Column(SMALLINT, nullable=True)


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    is_fahrenheit = Column(Boolean, nullable=False)
    is_imperial = Column(Boolean, nullable=False)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    latitude = Column(DECIMAL(9, 6), nullable=True)
    longitude = Column(DECIMAL(9, 6), nullable=True)
    garage_alert_time = Column(Integer, nullable=False, server_default='0')
    garage_node_id = Column(UUID, ForeignKey(DeviceNodes.id), nullable=True)

    user = relationship('UserInformation', foreign_keys='UserPreference.user_id')
    garage_node = relationship('DeviceNodes', foreign_keys='UserPreference.garage_node_id')


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


class DailySumpPumpLevel(Base):
    __tablename__ = 'daily_sump_level'

    id = Column(Integer, nullable=False, primary_key=True)
    device_id = Column(UUID, ForeignKey(Devices.id))
    distance = Column(DECIMAL, nullable=False)
    warning_level = Column(Integer, nullable=False)
    create_date = Column(TIMESTAMP, nullable=False)

    device = relationship('Devices', foreign_keys='DailySumpPumpLevel.device_id')


class AverageSumpPumpLevel(Base):
    __tablename__ = 'average_daily_sump_level'

    id = Column(Integer, nullable=False, primary_key=True)
    device_id = Column(UUID, ForeignKey(Devices.id))
    distance = Column(DECIMAL, nullable=False)
    create_day = Column(DATE, nullable=False)

    device = relationship('Devices', foreign_keys='AverageSumpPumpLevel.device_id')
