import json
import uuid

from mock import patch

from svc.models.app import Preference
from svc.models.sump import SumpLevel
from svc.controllers.sump_controller import get_sump_level, save_current_level


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
class TestSumpController:

    def setup_method(self):
        self.IMPERIAL_PREFERENCE = Preference(isImperial=True, isFahrenheit=True, garageId=1, garageDoor='Jons', tempUnit='Fahrenheit', measureUnit='in', city='Austin')
        self.METRIC_PREFERENCE = Preference(isImperial=False, isFahrenheit=False, garageId=2, garageDoor='Kals', tempUnit='Celsius', measureUnit='cm', city='Austin')

    def test_get_sump_level__should_call_get_current_sump_level_by_user(self, mock_database, mock_jwt):
        user_id = uuid.uuid4().hex
        bearer_token = 'abdsadf2345'
        get_sump_level(user_id, bearer_token)

        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.assert_called_with(user_id)

    def test_get_sump_level__should_return_response_with_distance(self, mock_database, mock_jwt):
        distance = 3.14159
        bearer_token = 'asdflkhsad98778236'
        user_id = 'fake12354'
        mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.METRIC_PREFERENCE
        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': distance, 'warningLevel': 0}
        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': distance, 'testItem': 123}

        actual = get_sump_level(user_id, bearer_token)

        assert actual == SumpLevel(currentDepth=distance, depthUnit='cm', warningLevel=0, averageDepth=distance)

    def test_get_sump_level__should_return_response_with_distance_converted_to_imperial(self, mock_database, mock_jwt):
        current_distance = 2.54
        average_distance = 5.08
        bearer_token = 'asdflkhsad98778236'
        user_id = 'fake12354'
        mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.IMPERIAL_PREFERENCE
        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': current_distance, 'warningLevel': 0}
        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': average_distance, 'testItem': 123}

        actual = get_sump_level(user_id, bearer_token)

        assert actual == SumpLevel(currentDepth=1.0, depthUnit='in', warningLevel=0, averageDepth=2.0)

    def test_get_sump_level__should_call_is_jwt_valid(self, mock_database, mock_jwt):
        user_id = 'fake1234'
        bearer_token = 'lkhasdhlufiou0892390784'

        get_sump_level(user_id, bearer_token)

        mock_jwt.assert_called_with(bearer_token)

    def test_get_sump_level__should_call_get_preferences_by_user(self, mock_database, mock_jwt):
        user_id = 'fake1234'
        bearer_token = 'lkhasdhlufiou0892390784'

        get_sump_level(user_id, bearer_token)

        mock_database.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(user_id)

    def test_get_sump_level__should_call_get_average_sump_level_by_user(self, mock_database, mock_jwt):
        user_id = 'fake1234'
        bearer_token = 'lkhasdhlufiou0892390784'

        get_sump_level(user_id, bearer_token)

        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.assert_called_with(user_id)

    def test_save_current_level__should_call_is_jwt_valid(self, mock_db, mock_jwt):
        user_id = 1234
        bearer_token = 'fake_token'
        request = json.dumps({'depth': 'test'})

        save_current_level(user_id, bearer_token, request)

        mock_jwt.assert_called_with(bearer_token)

    def test_save_current_level__should_call_save_current_sump_level(self, mock_db, mock_jwt):
        user_id = 1234
        bearer_token = 'fake_token'
        depth_info = {'depth': 'test'}
        request = json.dumps(depth_info)

        save_current_level(user_id, bearer_token, request)

        mock_db.return_value.__enter__.return_value.insert_current_sump_level.assert_called_with(user_id, depth_info)
