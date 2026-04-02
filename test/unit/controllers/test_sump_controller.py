from mock import patch

from svc.constants.home_automation import AuthClaims
from svc.models.app import Preference
from svc.models.sump import SumpLevel
from svc.controllers.sump_controller import get_sump_level, save_current_level


@patch('svc.controllers.sump_controller.AuthClient')
@patch('svc.controllers.sump_controller.SumpDatabase')
class TestSumpController:
    USER_ID = 'fake1234'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = 'lkhasdhlufiou0892390784'

    def setup_method(self):
        self.IMPERIAL_PREFERENCE = Preference(isImperial=True, isFahrenheit=True, garageId=1, garageDoor='Jons', tempUnit='Fahrenheit', measureUnit='in', city='Austin')
        self.METRIC_PREFERENCE = Preference(isImperial=False, isFahrenheit=False, garageId=2, garageDoor='Kals', tempUnit='Celsius', measureUnit='cm', city='Austin')

    def test_get_sump_level__should_call_get_current_sump_level_by_user(self, mock_database, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_return_response_with_distance(self, mock_database, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        distance = 3.14159
        mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.METRIC_PREFERENCE
        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': distance, 'warningLevel': 0}
        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': distance, 'testItem': 123}

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=distance, depthUnit='cm', warningLevel=0, averageDepth=distance)

    def test_get_sump_level__should_return_response_with_distance_converted_to_imperial(self, mock_database, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        current_distance = 2.54
        average_distance = 5.08
        mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.IMPERIAL_PREFERENCE
        mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': current_distance, 'warningLevel': 0}
        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': average_distance, 'testItem': 123}

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=1.0, depthUnit='in', warningLevel=0, averageDepth=2.0)

    def test_get_sump_level__should_call_is_jwt_valid(self, mock_database, mock_jwt):
        get_sump_level(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_sump_level__should_call_get_preferences_by_user(self, mock_database, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_database.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_call_get_average_sump_level_by_user(self, mock_database, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.assert_called_with(self.USER_ID)

    def test_save_current_level__should_call_is_jwt_valid(self, mock_db, mock_jwt):
        request_data = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, request_data)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_save_current_level__should_call_save_current_sump_level(self, mock_db, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        depth_info = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, depth_info)

        mock_db.return_value.__enter__.return_value.insert_current_sump_level.assert_called_with(self.USER_ID, depth_info)
