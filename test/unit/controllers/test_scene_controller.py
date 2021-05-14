import uuid

from mock import patch

from svc.controllers.scene_controller import get_created_scenes, delete_created_scene


@patch('svc.controllers.scene_controller.UserDatabaseManager')
@patch('svc.controllers.scene_controller.is_jwt_valid')
class TestSceneController:
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    BEARER_TOKEN = 'fake bearer token'

    def test_get_created_scenes__should_validate_jwt(self, mock_jwt, mock_db):
        get_created_scenes(self.BEARER_TOKEN, self.USER_ID)
        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_created_scenes__should_quer_database_for_records(self, mock_jwt, mock_db):
        get_created_scenes(self.BEARER_TOKEN, self.USER_ID)
        mock_db.return_value.__enter__.return_value.get_scenes_by_user.assert_called_with(self.USER_ID)

    def test_get_created_scenes__should_return_response_from_database(self, mock_jwt, mock_db):
        response = {'test_record': 'doesnt matter'}
        mock_db.return_value.__enter__.return_value.get_scenes_by_user.return_value = response
        actual = get_created_scenes(self.BEARER_TOKEN, self.USER_ID)

        assert actual == response

    def test_delete_created_scene__should_validate_jwt(self, mock_jwt, mock_db):
        delete_created_scene(self.BEARER_TOKEN, self.USER_ID, self.SCENE_ID)
        mock_jwt.assert_called_with(self.BEARER_TOKEN)