from sqlalchemy import select
from werkzeug.exceptions import Unauthorized

from svc.db.models.user_information_model import UserInformation
from svc.db.repositories.database_base import DatabaseBase


#TODO: change password will need to call auth0 api
class CredentialRepository(DatabaseBase):

    def change_user_password(self, user_id, old_pass, new_pass):
        self._validate_property(user_id)
        # stmt = select(UserCredentials).filter_by(user_id=user_id)
        # user = self.session.execute(stmt).scalars().first()
        # if user.password != old_pass:
        #     raise Unauthorized
        # user.password = new_pass

    def get_user_info(self, user_id):
        stmt = select(UserInformation).filter_by(id=user_id)
        user = self.session.execute(stmt).scalars().first()
        if user is None:
            raise Unauthorized
        return {'user_id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name}