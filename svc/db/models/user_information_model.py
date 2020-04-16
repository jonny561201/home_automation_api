import sqlalchemy
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DECIMAL, TIMESTAMP, DATE
from sqlalchemy.dialects.postgresql import UUID, INET, SMALLINT
from sqlalchemy.ext import declarative
from sqlalchemy.orm import relationship

Base = declarative.declarative_base()


class UserInformation(Base):
    __tablename__ = 'user_information'

    id = Column(UUID, nullable=False, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=True)


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

    # role_device = relationship('RoleDevices', cascade='delete', foreign_keys='RoleDeviceNodes.role_device_id')


class UserPreference(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(UUID, ForeignKey(UserInformation.id))
    is_fahrenheit = Column(Boolean, nullable=False)
    is_imperial = Column(Boolean, nullable=False)
    city = Column(String, nullable=True)

    user = relationship('UserInformation', foreign_keys='UserPreference.user_id')


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
