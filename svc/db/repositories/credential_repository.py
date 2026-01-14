import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select, delete
from werkzeug.exceptions import Unauthorized, Forbidden

from svc.db.repositories.database_base import DatabaseBase
from svc.db.models.user_information_model import UserCredentials, RefreshToken


class CredentialRepository(DatabaseBase):

    def validate_credentials(self, user_name, pword):
        stmt = select(UserCredentials).filter_by(user_name=user_name)
        user = self.session.execute(stmt).scalars().first()
        if user is None or user.password != pword:
            raise Unauthorized
        return {'user_id': str(user.user_id),
                'roles': [self._create_role(role.role_devices, role.role.role_name) for role in user.user_roles],
                'first_name': user.user.first_name,
                'last_name': user.user.last_name}

    def insert_refresh_token(self, user_id, refresh_token, expire):
        self.session.execute(delete(RefreshToken).where(RefreshToken.user_id == user_id))
        token = RefreshToken(refresh=refresh_token, count=10, user_id=user_id, expire_time=expire)
        self.session.add(token)

    def generate_new_refresh_token(self, refresh_token, expire):
        stmt = select(RefreshToken).filter_by(refresh=refresh_token)
        token = self.session.execute(stmt).scalars().first()
        if token is None or token.expire_time < datetime.now(tz=ZoneInfo('US/Central')) or token.count <= 0:
            raise Forbidden
        new_refresh = str(uuid.uuid4())
        token.refresh = new_refresh
        token.expire_time = expire
        token.count -= 1
        return {'user_id': str(token.user_id), 'refresh_token': new_refresh}

    def change_user_password(self, user_id, old_pass, new_pass):
        self._validate_property(user_id)
        stmt = select(UserCredentials).filter_by(user_id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user.password != old_pass:
            raise Unauthorized
        user.password = new_pass

    def get_user_info(self, user_id):
        stmt = select(UserCredentials).filter_by(user_id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user is None:
            raise Unauthorized
        return {'user_id': str(user.user_id),
                'roles': [self._create_role(role.role_devices, role.role.role_name) for role in user.user_roles],
                'first_name': user.user.first_name,
                'last_name': user.user.last_name}