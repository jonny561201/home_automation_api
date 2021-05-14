from mock import patch

from svc.controllers.scene_controller import get_created_scenes


@patch('svc.controllers.scene_controller.is_jwt_valid')
def test_get_created_scenes__should_validate_jwt(mock_jwt):
    bearer_token = 'fake bearer token'
    get_created_scenes(bearer_token)
    mock_jwt.assert_called_with(bearer_token)