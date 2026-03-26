import uuid

from sqlalchemy import delete, select

from db.models.user_information_model import UserInformation, Scenes, SceneDetails
from db.repositories.database_base import DatabaseBase
from db.repositories.lights_repository import LightsRepository
from models.scenes import LightScenes


class TestUserScenes:
    SCENE_ID = str(uuid.uuid4())
    USER_ID = str(uuid.uuid4())
    SCENE_NAME = 'Movie'
    GROUP_NAME = 'living room'

    def setup_method(self):
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

    def test_get_scenes_by_user__should_return_records(self):
        with LightsRepository() as database:
            actual = database.get_scenes_by_user(self.USER_ID)

        assert actual.scenes[0].name == self.SCENE_NAME
        assert actual.scenes[0].lights[0].groupName == self.GROUP_NAME

    def test_get_scenes_by_user__should_return_empty_list_when_none(self):
        with LightsRepository() as database:
            actual = database.get_scenes_by_user(str(uuid.uuid4()))

        assert actual.to_dict() == LightScenes(scenes=[]).to_dict()

    def test_delete_scene_by_user__should_delete_record(self):
        with LightsRepository() as database:
            database.delete_scene_by_user(self.USER_ID, self.SCENE_ID)

        with LightsRepository() as database:
            actual = database.session.execute(select(Scenes).where(Scenes.user_id == self.USER_ID)).scalars().all()
            assert len(actual) == 0
