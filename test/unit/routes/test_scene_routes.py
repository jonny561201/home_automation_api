import json
import uuid

from mock import patch, ANY

from svc.routes.scene_routes import get_scenes_by_user, delete_scene_by_user


@patch('svc.routes.scene_routes.request')
@patch('svc.routes.scene_routes.scene_controller')
class TestSceneRoutes:
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    BEARER_TOKEN = 'im a bearer token'
    RESPONSE = {'response': 'Im a fake response'}

    def test_get_scenes_by_user__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        get_scenes_by_user(self.USER_ID)

        mock_controller.get_created_scenes.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_get_scenes_by_user__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        get_scenes_by_user(self.USER_ID)

        mock_controller.get_created_scenes.assert_called_with(ANY, self.USER_ID)

    def test_get_scenes_by_user__should_call_controller_when_no_auth_header(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {}
        get_scenes_by_user(self.USER_ID)

        mock_controller.get_created_scenes.assert_called_with(None, self.USER_ID)

    def test_get_scenes_by_user__should_return_success_status_code(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        actual = get_scenes_by_user(self.USER_ID)

        assert actual.status_code == 200

    def test_get_scenes_by_user__should_return_content_type(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        actual = get_scenes_by_user(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_get_scenes_by_user__should_return_response_from_controller(self, mock_controller, mock_request):
        mock_controller.get_created_scenes.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        actual = get_scenes_by_user(self.USER_ID)

        assert json.loads(actual.data) == self.RESPONSE

    def test_delete_scene_by_user__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_controller.delete_created_scene.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        delete_scene_by_user(self.USER_ID, self.SCENE_ID)

        mock_controller.delete_created_scene.assert_called_with(self.BEARER_TOKEN, ANY, ANY)

    def test_delete_scene_by_user__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_controller.delete_created_scene.return_value = self.RESPONSE
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        delete_scene_by_user(self.USER_ID, self.SCENE_ID)

        mock_controller.delete_created_scene.assert_called_with(ANY, self.USER_ID, ANY)

