import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest

from svc.db.repositories.push_subscription_repository import PushSubscriptionRepository


class TestPushSubscriptionRepository:
    USER_ID = '1234abcd'
    ENDPOINT = 'https://fcm.googleapis.com/fcm/send/abc123'
    P256DH_KEY = 'BNcvalueforp256dh'
    AUTH_KEY = 'tBHIauthkeyvalue'

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = PushSubscriptionRepository()
        self.DATABASE.session = self.SESSION

    def test_upsert_subscription__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.upsert_subscription(None, self.ENDPOINT, self.P256DH_KEY, self.AUTH_KEY)
        self.SESSION.execute.assert_not_called()

    def test_upsert_subscription__should_execute_statement(self):
        self.DATABASE.upsert_subscription(self.USER_ID, self.ENDPOINT, self.P256DH_KEY, self.AUTH_KEY)

        self.SESSION.execute.assert_called_once()

    def test_delete_subscription__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_subscription(None, self.ENDPOINT)
        self.SESSION.execute.assert_not_called()

    def test_delete_subscription__should_raise_bad_request_when_endpoint_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_subscription(self.USER_ID, None)
        self.SESSION.execute.assert_not_called()

    def test_delete_subscription__should_execute_statement(self):
        self.DATABASE.delete_subscription(self.USER_ID, self.ENDPOINT)

        self.SESSION.execute.assert_called_once()
