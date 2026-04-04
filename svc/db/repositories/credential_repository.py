from sqlalchemy import select
from werkzeug.exceptions import Unauthorized

from svc.db.models.user_information_model import UserInformation
from svc.db.repositories.database_base import DatabaseBase


class CredentialRepository(DatabaseBase):

    def get_user_info(self, user_id):
        stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user is None:
            raise Unauthorized
        return {'user_id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name}