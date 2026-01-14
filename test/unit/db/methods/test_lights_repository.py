import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import mock
import pytest
from sqlalchemy import orm
from werkzeug.exceptions import BadRequest

from svc.db.models.user_information_model import SceneDetails, Scenes
from svc.models.scenes import LightScenes
from svc.db.repositories.lights_repository import LightsRepository


class TestLightsRepository:
    USER_ID = '1234abcd'
    NOW = datetime.now(tz=ZoneInfo('US/Central'))

    def setup_method(self, _):
        self.SESSION = mock.create_autospec(orm.scoped_session)
        self.DATABASE = LightsRepository()
        self.DATABASE.session = self.SESSION

    def test_get_scenes_by_user__should__should_query_for_scenes_by_user_id(self):
        self.DATABASE.get_scenes_by_user(self.USER_ID)
        self.SESSION.execute.return_value.unique.return_value.scalars.return_value.all.assert_called()

    def test_get_scenes_by_user__should_return_user_data(self):
        scene = Scenes()
        scene_name = 'my test name'
        scene.name = scene_name
        detail = SceneDetails()
        room_name = 'fake room'
        detail.light_group_name = room_name
        scene.details = [detail]
        self.SESSION.execute.return_value.unique.return_value.scalars.return_value.all.return_value = [scene]
        actual = self.DATABASE.get_scenes_by_user(self.USER_ID)

        assert actual.scenes[0].name == scene_name
        assert actual.scenes[0].lights[0].groupName == room_name

    def test_get_scenes_by_user__should_return_empty_list_when_query_returns_none(self):
        self.SESSION.execute.return_value.scalars.return_value.all.return_value = None
        actual = self.DATABASE.get_scenes_by_user(self.USER_ID)

        assert actual.to_dict() == LightScenes(scenes=[]).to_dict()

    def test_get_scenes_by_user__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_scenes_by_user(None)

    def test_get_scenes_by_user__should_not_call_database_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.get_scenes_by_user(None)
        self.SESSION.query.assert_not_called()

    def test_delete_scene_by_user__should_raise_bad_request_when_user_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_scene_by_user(None, str(uuid.uuid4()))
        self.SESSION.query.assert_not_called()

    def test_delete_scene_by_user__should_raise_bad_request_when_scene_id_is_none(self):
        with pytest.raises(BadRequest):
            self.DATABASE.delete_scene_by_user(self.USER_ID, None)
        self.SESSION.query.assert_not_called()

    def test_delete_scene_by_user__should_query_to_delete_scene(self):
        scene_id = str(uuid.uuid4())
        self.DATABASE.delete_scene_by_user(self.USER_ID, scene_id)

        self.SESSION.execute.assert_called()

    def test_delete_scene_by_user__should_query_to_delete_scene_detail(self):
        scene_id = str(uuid.uuid4())
        self.DATABASE.delete_scene_by_user(self.USER_ID, scene_id)

        assert self.SESSION.execute.call_count == 2