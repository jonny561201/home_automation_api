from sqlalchemy import select
from werkzeug.exceptions import Unauthorized

from svc.db.models.user_information_model import UserCredentials
from svc.db.repositories.database_base import DatabaseBase


class CredentialRepository(DatabaseBase):

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