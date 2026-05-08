import json
import uuid

from sqlalchemy import delete, select

from svc.db.models.user_information_model import PushSubscription, UserInformation
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import create_app
from test.integration.integration_helpers import mock_jwks_token


class TestPushRoutesIntegration:
    USER_ID = str(uuid.uuid4())
    ENDPOINT = 'https://fcm.googleapis.com/fcm/send/integration-test-abc'
    P256DH_KEY = 'BNcintegrationp256dhvalue'
    AUTH_KEY = 'tBHIintegrationauthvalue'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADERS = {'Authorization': f'Bearer {self.TOKEN}', 'Content-Type': 'application/json'}
        flask_app = create_app()
        self.TEST_CLIENT = flask_app.test_client()
        self.USER = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')

        with DatabaseBase() as database:
            database.session.add(self.USER)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(PushSubscription).where(PushSubscription.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_subscribe__should_return_unauthorized_when_no_bearer_token(self):
        body = json.dumps({'endpoint': self.ENDPOINT, 'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}})
        actual = self.TEST_CLIENT.post('notifications/subscribe', data=body, headers={'Content-Type': 'application/json'})

        assert actual.status_code == 401

    def test_subscribe__should_return_bad_request_when_endpoint_missing(self):
        body = json.dumps({'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}})
        actual = self.TEST_CLIENT.post('notifications/subscribe', data=body, headers=self.HEADERS)

        assert actual.status_code == 400

    def test_subscribe__should_persist_new_subscription(self):
        body = json.dumps({'endpoint': self.ENDPOINT, 'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}})
        actual = self.TEST_CLIENT.post('notifications/subscribe', data=body, headers=self.HEADERS)

        assert actual.status_code == 200
        with DatabaseBase() as database:
            stmt = select(PushSubscription).where(PushSubscription.endpoint == self.ENDPOINT)
            row = database.session.execute(stmt).scalars().first()
            assert str(row.user_id) == self.USER_ID
            assert row.p256dh_key == self.P256DH_KEY
            assert row.auth_key == self.AUTH_KEY

    def test_subscribe__should_update_existing_subscription_when_endpoint_repeats(self):
        first_body = json.dumps({'endpoint': self.ENDPOINT, 'keys': {'p256dh': 'old_p256', 'auth': 'old_auth'}})
        self.TEST_CLIENT.post('notifications/subscribe', data=first_body, headers=self.HEADERS)
        second_body = json.dumps({'endpoint': self.ENDPOINT, 'keys': {'p256dh': self.P256DH_KEY, 'auth': self.AUTH_KEY}})

        actual = self.TEST_CLIENT.post('notifications/subscribe', data=second_body, headers=self.HEADERS)

        assert actual.status_code == 200
        with DatabaseBase() as database:
            stmt = select(PushSubscription).where(PushSubscription.endpoint == self.ENDPOINT)
            rows = database.session.execute(stmt).scalars().all()
            assert len(rows) == 1
            assert rows[0].p256dh_key == self.P256DH_KEY
            assert rows[0].auth_key == self.AUTH_KEY
