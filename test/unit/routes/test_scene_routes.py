import uuid

from mock import patch, ANY

from svc.routes.scene_routes import get_scenes_by_user


@patch('svc.routes.scene_routes.request')
@patch('svc.routes.scene_routes.get_created_scenes')
class TestSceneRoutes:
    USER_ID = str(uuid.uuid4())
    BEARER_TOKEN = 'im a bearer token'

    def test_get_scenes_by_user__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        get_scenes_by_user(self.USER_ID)

        mock_controller.assert_called_with(self.BEARER_TOKEN, ANY)

    def test_get_scenes_by_user__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        get_scenes_by_user(self.USER_ID)

        mock_controller.assert_called_with(ANY, self.USER_ID)

    def test_get_scenes_by_user__should_call_controller_when_no_auth_header(self, mock_controller, mock_request):
        mock_request.headers = {}
        get_scenes_by_user(self.USER_ID)

        mock_controller.assert_called_with(None, self.USER_ID)

    def test_get_scenes_by_user__should_return_success_status_code(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.BEARER_TOKEN}
        actual = get_scenes_by_user(self.USER_ID)

        assert actual.status_code == 200

