from sqlalchemy import delete, select, or_
from sqlalchemy.dialects.postgresql import insert
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import ChildAccounts, PushSubscription
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

    def delete_subscription_by_endpoint(self, endpoint):
        if endpoint is None:
            raise BadRequest()
        stmt = delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
        self.session.execute(stmt)

    def get_subscriptions_for_household(self, parent_user_id):
        if parent_user_id is None:
            raise BadRequest()
        child_subq = select(ChildAccounts.child_user_id).where(ChildAccounts.parent_user_id == parent_user_id)
        stmt = select(PushSubscription).where(or_(PushSubscription.user_id == parent_user_id, PushSubscription.user_id.in_(child_subq)))
        return self.session.execute(stmt).scalars().all()
