import json
import uuid

from sqlalchemy import delete

from integration.integration_helpers import mock_jwks_token
from svc.db.models.user_information_model import Scenes, SceneDetails, UserInformation
from svc.db.repositories.database_base import DatabaseBase
from svc.manager import app


class TestSceneRoutes:
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    SCENE_NAME = 'movie timez'
    GROUP_NAME = 'livin in the room'

    def setup_method(self):
        self.TOKEN = mock_jwks_token(self.USER_ID)
        self.HEADER = {'Authorization': f'Bearer {self.TOKEN}', 'Content-Type': 'application/json'}

        flask_app = app
        self.TEST_CLIENT = flask_app.test_client()
        self.USER_INFO = UserInformation(id=self.USER_ID, first_name='tony', last_name='stark')
        self.SCENE = Scenes(name=self.SCENE_NAME, user_id=self.USER_ID, id=self.SCENE_ID)
        self.DETAIL = SceneDetails(light_group='2', light_group_name=self.GROUP_NAME, light_brightness=45, scene_id=self.SCENE_ID)
        with DatabaseBase() as database:
            database.session.add(self.USER_INFO)
            database.session.commit()
            database.session.add(self.SCENE)
            database.session.add(self.DETAIL)

    def teardown_method(self):
        with DatabaseBase() as database:
            database.session.execute(delete(SceneDetails).where(SceneDetails.scene_id == self.SCENE_ID))
            database.session.execute(delete(Scenes).where(Scenes.id == self.SCENE_ID))
            database.session.execute(delete(UserInformation).where(UserInformation.id == self.USER_ID))

    def test_get_scenes_by_user__should_return_success_response(self):
        actual = self.TEST_CLIENT.get(f'scenes/list', headers=self.HEADER)

        assert actual.status_code == 200
        assert json.loads(actual.data)['scenes'][0]['name'] == self.SCENE_NAME
        assert json.loads(actual.data)['scenes'][0]['lights'][0]['groupName'] == self.GROUP_NAME

    def test_get_scenes_by_user__should_return_unauthorized_with_no_header(self):
        actual = self.TEST_CLIENT.get(f'scenes/list')

        assert actual.status_code == 401

    def test_delete_scene_by_user__should_remove_existing_record(self):
        actual = self.TEST_CLIENT.delete(f'scenes/{self.SCENE_ID}', headers=self.HEADER)

        assert actual.status_code == 200

    def test_delete_scene_by_user__should_return_unauthorized_with_no_header(self):
        actual = self.TEST_CLIENT.delete(f'scenes/{self.SCENE_ID}')

        assert actual.status_code == 401
