import json
import uuid
from datetime import datetime

from sqlalchemy import select, delete

from integration.integration_helpers import mock_jwks_token
from svc.db.models.user_information_model import UserInformation, DailySumpPumpLevel, AverageSumpPumpLevel, \
    UserPreference
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestSumpRoutes:
    USER_ID = str(uuid.uuid4())
    DEPTH = 12.45
    AVG_DEPTH = 10.65

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADER = {'Authorization': f'Bearer {self.TOKEN}', 'Content-Type': 'application/json'}

        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        user = UserInformation(id=self.USER_ID, first_name='Jon', last_name='Test')
        preference = UserPreference(user=user, is_imperial=False, is_fahrenheit=True)
        sump = DailySumpPumpLevel(user=user, distance=self.DEPTH, warning_level=0, create_date=datetime.now())
        average = AverageSumpPumpLevel(user=user, distance=self.AVG_DEPTH, create_day=datetime.date(datetime.now()))

        with DatabaseBase() as database:
            database.session.add(sump)
            database.session.add(preference)
            database.session.add(average)
            database.session.flush()

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(DailySumpPumpLevel).where(DailySumpPumpLevel.user_id == self.USER_ID))
            database.session.execute(delete(AverageSumpPumpLevel).where(AverageSumpPumpLevel.user_id == self.USER_ID))
            database.session.execute(delete(UserPreference).where(UserPreference.user_id == self.USER_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_current_sump_level__should_return_not_found_when_user_does_not_exist(self):
        token = mock_jwks_token(str(uuid.uuid4()))
        header = {'Authorization': f'Bearer {token}'}
        actual = self.TEST_CLIENT.get(f'sumpPump/depth', headers=header)

        assert actual.status_code == 404

    def test_get_current_sump_level__should_raise_unauthorized_when_invalid_user(self):
        actual = self.TEST_CLIENT.get(f'sumpPump/depth', headers={})

        assert actual.status_code == 401

    def test_get_current_sump_level__should_return_valid_response(self):
        actual = self.TEST_CLIENT.get(f'sumpPump/depth', headers=self.HEADER)
        json_actual = json.loads(actual.data)

        assert actual.status_code == 200
        assert json_actual['currentDepth'] == self.DEPTH
        assert json_actual['averageDepth'] == self.AVG_DEPTH

    def test_save_current_level_by_user__should_store_depth_info(self):
        depth = 12.31
        post_body = {'depth': depth, 'warning_level': 2, 'datetime': str(datetime.now())}

        self.TEST_CLIENT.post(f'sumpPump/currentDepth', data=json.dumps(post_body), headers=self.HEADER)

        with DatabaseBase() as database:
            sump_level = database.session.execute(select(DailySumpPumpLevel).where(DailySumpPumpLevel.user_id == self.USER_ID, DailySumpPumpLevel.distance == depth)).scalars().first()
            assert float(sump_level.distance) == depth
            assert str(sump_level.user_id) == self.USER_ID
