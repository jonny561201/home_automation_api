import uuid

from mock import patch

from svc.constants.home_automation import AuthClaims
from svc.controllers.scene_controller import create_scene, get_created_scenes, delete_created_scene


@patch('svc.controllers.scene_controller.LightsRepository')
@patch('svc.controllers.scene_controller.AuthClient')
class TestSceneController:
    USER_ID = str(uuid.uuid4())
    SCENE_ID = str(uuid.uuid4())
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = 'fake bearer token'

    REQUEST = {'name': 'Movie Night', 'details': [{'groupId': '1', 'brightness': 50}]}

    def test_create_scene__should_validate_jwt(self, mock_jwt, mock_db):
        create_scene(self.BEARER_TOKEN, self.REQUEST)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_create_scene__should_call_database_to_create_record(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        create_scene(self.BEARER_TOKEN, self.REQUEST)
        mock_db.return_value.__enter__.return_value.create_scene.assert_called_with(self.USER_ID, self.REQUEST)

    def test_create_scene__should_return_response_from_database(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        response = {'test_record': 'doesnt matter'}
        mock_db.return_value.__enter__.return_value.create_scene.return_value = response
        actual = create_scene(self.BEARER_TOKEN, self.REQUEST)

        assert actual == response

    def test_get_created_scenes__should_validate_jwt(self, mock_jwt, mock_db):
        get_created_scenes(self.BEARER_TOKEN)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_created_scenes__should_query_database_for_records(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_created_scenes(self.BEARER_TOKEN)
        mock_db.return_value.__enter__.return_value.get_scenes_by_user.assert_called_with(self.USER_ID)

    def test_get_created_scenes__should_return_response_from_database(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        response = {'test_record': 'doesnt matter'}
        mock_db.return_value.__enter__.return_value.get_scenes_by_user.return_value = response
        actual = get_created_scenes(self.BEARER_TOKEN)

        assert actual == response

    def test_delete_created_scene__should_validate_jwt(self, mock_jwt, mock_db):
        delete_created_scene(self.BEARER_TOKEN, self.SCENE_ID)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_delete_created_scene__should_query_database_to_delete_record(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        delete_created_scene(self.BEARER_TOKEN, self.SCENE_ID)
        mock_db.return_value.__enter__.return_value.delete_scene_by_user.assert_called_with(self.USER_ID, self.SCENE_ID)