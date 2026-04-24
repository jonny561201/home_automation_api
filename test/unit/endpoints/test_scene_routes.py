import json
import uuid

from mock import patch, ANY
from flask import Flask

from svc.models.scenes import LightScene, LightDetail, LightScenes
from svc.endpoints.scene_routes import create_scene, get_scenes, delete_scene


@patch('svc.endpoints.scene_routes.scene_controller')
class TestSceneRoutes:
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    BEARER_TOKEN = 'im a bearer token'

    REQUEST_BODY = {'name': 'Movie Night', 'details': [{'groupId': '1', 'brightness': 50}]}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context(headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()
        self.SCENE = LightScene(id=self.SCENE_ID, name='test', lights=[(LightDetail(groupId=1, groupName='test light', brightness=75))])
        self.SCENES = LightScenes(scenes=[self.SCENE])

    def teardown_method(self):
        self.ctx.pop()

    def test_create_scene__should_call_controller_with_bearer_token(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(json=self.REQUEST_BODY, headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()
        mock_controller.create_scene.return_value = self.SCENE
        create_scene()

        mock_controller.create_scene.assert_called_with(self.BEARER_TOKEN, self.REQUEST_BODY)

    def test_create_scene__should_call_controller_with_none_when_bearer_token_missing(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(json=self.REQUEST_BODY)
        self.ctx.push()
        mock_controller.create_scene.return_value = self.SCENE
        create_scene()

        mock_controller.create_scene.assert_called_with(None, self.REQUEST_BODY)

    def test_create_scene__should_return_success_status_code(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(json=self.REQUEST_BODY, headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()
        mock_controller.create_scene.return_value = self.SCENE
        actual = create_scene()

        assert actual.status_code == 200

    def test_create_scene__should_return_content_type(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(json=self.REQUEST_BODY, headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()
        mock_controller.create_scene.return_value = self.SCENE
        actual = create_scene()

        assert actual.content_type == 'application/json'

    def test_create_scene__should_return_response_from_controller(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context(json=self.REQUEST_BODY, headers={'Authorization': self.BEARER_TOKEN})
        self.ctx.push()
        mock_controller.create_scene.return_value = self.SCENE
        actual = create_scene()

        assert json.loads(actual.data) == self.SCENE.to_dict()

    def test_get_scenes__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_created_scenes.return_value = self.SCENES
        get_scenes()

        mock_controller.get_created_scenes.assert_called_with(self.BEARER_TOKEN)

    def test_get_scenes__should_call_controller_when_no_auth_header(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        mock_controller.get_created_scenes.return_value = self.SCENES
        get_scenes()

        mock_controller.get_created_scenes.assert_called_with(None)

    def test_get_scenes__should_return_success_status_code(self, mock_controller):
        mock_controller.get_created_scenes.return_value = self.SCENES
        actual = get_scenes()

        assert actual.status_code == 200

    def test_get_scenes__should_return_content_type(self, mock_controller):
        mock_controller.get_created_scenes.return_value = self.SCENES
        actual = get_scenes()

        assert actual.content_type == 'application/json'

    def test_get_scenes__should_return_response_from_controller(self, mock_controller):
        mock_controller.get_created_scenes.return_value = self.SCENES
        actual = get_scenes()

        assert json.loads(actual.data) == self.SCENES.to_dict()

    def test_delete_scene__should_call_controller_with_bearer_token(self, mock_controller):
        delete_scene(self.SCENE_ID)

        mock_controller.delete_created_scene.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_delete_scene__should_call_controller_with_none_when_bearer_token_missing(self, mock_controller):
        self.ctx.pop()
        self.ctx = self.app.test_request_context()
        self.ctx.push()
        delete_scene(self.SCENE_ID)

        mock_controller.delete_created_scene.assert_called_with(None, ANY)

    def test_delete_scene__should_call_controller_with_scene_id(self, mock_controller):
        delete_scene(self.SCENE_ID)

        mock_controller.delete_created_scene.assert_called_with(ANY, self.SCENE_ID)

    def test_delete_scene__should_return_success_status_code(self, mock_controller):
        actual = delete_scene(self.SCENE_ID)

        assert actual.status_code == 200

    def test_delete_scene__should_return_content_type(self, mock_controller):
        actual = delete_scene(self.SCENE_ID)

        assert actual.content_type == 'application/json'
