import uuid

from mock import patch, ANY

from svc.routes.scene_routes import get_scenes_by_user


@patch('svc.routes.scene_routes.request')
@patch('svc.routes.scene_routes.get_created_scenes')
def test_get_scenes_by_user__should_call_controller_with_bearer_token(mock_controller, mock_request):
    user_id = str(uuid.uuid4())
    bearer_token = 'im a bearer token'
    mock_request.headers = {'Authorization': bearer_token}
    get_scenes_by_user(user_id)

    mock_controller.assert_called_with(bearer_token, ANY)