from mock import patch

from svc.constants.home_automation import AuthClaims
from svc.models.app import Preference
from svc.models.sump import SumpLevel
from svc.controllers.sump_controller import get_sump_level, save_current_level


@patch('svc.controllers.sump_controller.DeviceRepository')
@patch('svc.controllers.sump_controller.AuthClient')
@patch('svc.controllers.sump_controller.UserRepository')
@patch('svc.controllers.sump_controller.SumpRepository')
class TestSumpController:
    USER_ID = 'fake1234'
    DEVICE_ID = 'device5678'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = 'lkhasdhlufiou0892390784'

    def setup_method(self):
        self.IMPERIAL_PREFERENCE = Preference(isImperial=True, isFahrenheit=True, tempUnit='Fahrenheit', measureUnit='in', city='Austin')
        self.METRIC_PREFERENCE = Preference(isImperial=False, isFahrenheit=False, tempUnit='Celsius', measureUnit='cm', city='Austin')

    def test_get_sump_level__should_call_is_jwt_valid(self, mock_sump, mock_user, mock_jwt, mock_device):
        get_sump_level(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_sump_level__should_call_get_sump_device_id_by_user(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_device.return_value.__enter__.return_value.get_sump_device_id_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_call_get_current_sump_level_by_device(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_device.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        get_sump_level(self.BEARER_TOKEN)

        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.assert_called_with(self.DEVICE_ID)

    def test_get_sump_level__should_call_get_average_sump_level_by_device(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_device.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        get_sump_level(self.BEARER_TOKEN)

        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.assert_called_with(self.DEVICE_ID)

    def test_get_sump_level__should_call_get_preferences_by_user(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_user.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_return_response_with_distance(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        distance = 3.14159
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.METRIC_PREFERENCE
        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.return_value = {'currentDepth': distance, 'warningLevel': 0}
        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.return_value = {'averageDepth': distance, 'testItem': 123}

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=distance, depthUnit='cm', warningLevel=0, averageDepth=distance)

    def test_get_sump_level__should_return_response_with_distance_converted_to_imperial(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        current_distance = 2.54
        average_distance = 5.08
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.IMPERIAL_PREFERENCE
        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.return_value = {'currentDepth': current_distance, 'warningLevel': 0}
        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.return_value = {'averageDepth': average_distance, 'testItem': 123}

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=1.0, depthUnit='in', warningLevel=0, averageDepth=2.0)

    def test_save_current_level__should_call_get_device_id_by_api_key(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, depth_info)

        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.assert_called_with(self.BEARER_TOKEN)

    def test_save_current_level__should_call_insert_current_sump_level(self, mock_sump, mock_user, mock_jwt, mock_device):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, depth_info)

        mock_sump.return_value.__enter__.return_value.insert_current_sump_level.assert_called_with(self.DEVICE_ID, depth_info)
