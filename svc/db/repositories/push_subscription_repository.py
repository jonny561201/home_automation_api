from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import PushSubscription
from svc.db.repositories.database_base import DatabaseBase


class PushSubscriptionRepository(DatabaseBase):

    def upsert_subscription(self, user_id, endpoint, p256dh_key, auth_key):
        if user_id is None:
            raise BadRequest()
        stmt = insert(PushSubscription).values(user_id=user_id, endpoint=endpoint, p256dh_key=p256dh_key, auth_key=auth_key)
        stmt = stmt.on_conflict_do_update(index_elements=['endpoint'], set_={'user_id': user_id, 'p256dh_key': p256dh_key, 'auth_key': auth_key})
        self.session.execute(stmt)

    def delete_subscription(self, user_id, endpoint):
        if user_id is None or endpoint is None:
            raise BadRequest()
        stmt = delete(PushSubscription).where(PushSubscription.user_id == user_id, PushSubscription.endpoint == endpoint)
        self.session.execute(stmt)
