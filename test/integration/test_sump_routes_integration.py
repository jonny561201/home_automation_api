import json
import uuid
from datetime import datetime

import jwt

from svc.config.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import UserInformation, DailySumpPumpLevel, AverageSumpPumpLevel, \
    UserPreference
from svc.manager import app


class TestSumpRoutes:
    JWT_SECRET = 'fakeKey'

    def setup_method(self):
        Settings.get_instance()._settings = {'JwtSecret': self.JWT_SECRET}
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.BEAR_TOKEN = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        self.HEADER = {'Authorization': 'Bearer ' + self.BEAR_TOKEN.decode('UTF-8')}

    def test_get_current_sump_level__should_return_not_found_when_user_does_not_exist(self):
        user_id = uuid.uuid4().hex
        actual = self.TEST_CLIENT.get(f'sumpPump/user/{user_id}/depth', headers=self.HEADER)

        assert actual.status_code == 400

    def test_get_current_sump_level__should_raise_unauthorized_when_invalid_user(self):
        user_id = uuid.uuid4().hex
        actual = self.TEST_CLIENT.get(f'sumpPump/user/{user_id}/depth', headers={})

        assert actual.status_code == 401

    def test_get_current_sump_level__should_return_valid_response(self):
        user_id = uuid.uuid4().hex
        user = UserInformation(id=user_id, first_name='Jon', last_name='Test')
        expected_depth = 12.45
        average_depth = 10.65
        date = datetime.date(datetime.now())
        preference = UserPreference(user=user, is_imperial=False, is_fahrenheit=True)
        sump = DailySumpPumpLevel(user=user, distance=expected_depth, warning_level=0, create_date=datetime.now())
        average = AverageSumpPumpLevel(user=user, distance=average_depth, create_day=date)

        with UserDatabaseManager() as database:
            database.session.add(sump)
            database.session.add(preference)
            database.session.add(average)
            database.session.flush()

        actual = self.TEST_CLIENT.get(f'sumpPump/user/{user_id}/depth', headers=self.HEADER)
        json_actual = json.loads(actual.data)

        with UserDatabaseManager() as database:
            database.session.delete(sump)
            database.session.delete(preference)
            database.session.delete(user)
            database.session.delete(average)
            database.session.flush()

        assert actual.status_code == 200
        assert json_actual['currentDepth'] == expected_depth
        assert json_actual['averageDepth'] == average_depth

    def test_save_current_level_by_user__should_store_depth_info(self):
        depth = 12.31
        user_id = str(uuid.uuid4())
        post_body = {'depth': depth, 'warning_level': 2, 'datetime': str(datetime.now())}
        user = UserInformation(id=user_id, first_name='Jon', last_name='Test')
        with UserDatabaseManager() as database:
            database.session.add(user)

        self.TEST_CLIENT.post(f'sumpPump/user/{user_id}/currentDepth', data=json.dumps(post_body), headers=self.HEADER)

        with UserDatabaseManager() as database:
            sump_level = database.session.query(DailySumpPumpLevel).filter_by(user_id=user_id).first()
            assert float(sump_level.distance) == depth
            assert sump_level.user_id == user_id
