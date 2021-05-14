import json
import os
import uuid

import jwt

from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager
from svc.db.models.user_information_model import Scenes, SceneDetails, UserInformation
from svc.manager import app


class TestSceneRoutes:
    TEST_CLIENT = None
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    SCENE_NAME = 'movie timez'
    GROUP_NAME = 'livin in the room'
    JWT_SECRET = 'fakeKey'
    DB_USER = 'postgres'
    DB_PASS = 'password'
    DB_PORT = '5432'
    DB_NAME = 'garage_door'

    def setup_method(self):
        settings = Settings.get_instance()
        settings.dev_mode = False
        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.BEAR_TOKEN = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        self.HEADER = {'Authorization': 'Bearer ' + self.BEAR_TOKEN.decode('UTF-8')}
        os.environ.update({'JWT_SECRET': self.JWT_SECRET, 'SQL_USERNAME': self.DB_USER,
                           'SQL_PASSWORD': self.DB_PASS, 'SQL_DBNAME': self.DB_NAME,
                           'SQL_PORT': self.DB_PORT})
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.SCENE = Scenes(name=self.SCENE_NAME, user_id=self.USER_ID, id=self.SCENE_ID)
        self.DETAIL = SceneDetails(light_group='2', light_group_name=self.GROUP_NAME, light_brightness=45, scene_id=self.SCENE_ID)
        with UserDatabaseManager() as database:
            database.session.add(self.USER_INFO)
            database.session.commit()
            database.session.add(self.SCENE)
            database.session.add(self.DETAIL)

    def teardown_method(self):
        with UserDatabaseManager() as database:
            database.session.query(SceneDetails).delete()
            database.session.commit()
            database.session.query(Scenes).delete()
            database.session.delete(self.USER_INFO)
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_PORT')

    def test_get_scenes_by_user__should_return_success_response(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.get(f'scenes/userId/{self.USER_ID}', headers=headers)

        assert actual.status_code == 200
        assert json.loads(actual.data)[0]['name'] == self.SCENE_NAME
        assert json.loads(actual.data)[0]['lights'][0]['group_name'] == self.GROUP_NAME

    def test_get_scenes_by_user__should_return_unauthorized_with_no_header(self):
        url = f'scenes/userId/{self.USER_ID}'
        actual = self.TEST_CLIENT.get(url)

        assert actual.status_code == 401

    def test_delete_scene_by_user__should_remove_existing_record(self):
        bearer_token = jwt.encode({}, self.JWT_SECRET, algorithm='HS256')
        headers = {'Authorization': bearer_token}
        actual = self.TEST_CLIENT.delete(f'scenes/userId/{self.USER_ID}/scene/{self.SCENE_ID}', headers=headers)

        assert actual.status_code == 200
