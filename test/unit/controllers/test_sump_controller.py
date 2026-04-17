from decimal import Decimal

from mock import patch, MagicMock

from svc.constants.home_automation import AuthClaims
from svc.models.app import Preference
from svc.models.sump import SumpLevel
from svc.controllers.sump_controller import get_sump_level, save_current_level, save_average_level


@patch('svc.controllers.sump_controller.AuthClient')
@patch('svc.controllers.sump_controller.UserRepository')
@patch('svc.controllers.sump_controller.SumpRepository')
class TestSumpController:
    USER_ID = 'fake1234'
    DEVICE_ID = 'device5678'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = 'lkhasdhlufiou0892390784'

    def setup_method(self):
        self.IMPERIAL_PREFERENCE = Preference(tempUnit='fahrenheit', measureUnit='imperial', city='Austin')
        self.METRIC_PREFERENCE = Preference(tempUnit='celsius', measureUnit='metric', city='Austin')

    def test_get_sump_level__should_call_is_jwt_valid(self, mock_sump, mock_user, mock_jwt):
        get_sump_level(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_sump_level__should_call_get_sump_device_id_by_user(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_call_get_current_sump_level_by_device(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        get_sump_level(self.BEARER_TOKEN)

        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.assert_called_with(self.DEVICE_ID)

    def test_get_sump_level__should_call_get_average_sump_level_by_device(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        get_sump_level(self.BEARER_TOKEN)

        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.assert_called_with(self.DEVICE_ID)

    def test_get_sump_level__should_call_get_preferences_by_user(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        get_sump_level(self.BEARER_TOKEN)

        mock_user.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_sump_level__should_return_response_with_distance(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        distance = Decimal('3.14159')
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.METRIC_PREFERENCE
        current = MagicMock(distance=distance, warning_level=0)
        average = MagicMock(distance=distance, create_day=None)
        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.return_value = current
        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.return_value = average

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=float(distance), depthUnit='cm', warningLevel=0, averageDepth=float(distance))

    def test_get_sump_level__should_return_response_with_null_average_when_no_average_exists(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.METRIC_PREFERENCE
        current = MagicMock(distance=Decimal('3.14159'), warning_level=1)
        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.return_value = current
        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.return_value = None

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=float(Decimal('3.14159')), depthUnit='cm', warningLevel=1, averageDepth=None, latest_date=None)

    def test_get_sump_level__should_return_response_with_distance_converted_to_imperial(self, mock_sump, mock_user, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_user.return_value.__enter__.return_value.get_preferences_by_user.return_value = self.IMPERIAL_PREFERENCE
        current = MagicMock(distance=Decimal('2.54'), warning_level=0)
        average = MagicMock(distance=Decimal('5.08'), create_day=None)
        mock_sump.return_value.__enter__.return_value.get_current_sump_level_by_device.return_value = current
        mock_sump.return_value.__enter__.return_value.get_average_sump_level_by_device.return_value = average

        actual = get_sump_level(self.BEARER_TOKEN)

        assert actual == SumpLevel(currentDepth=1.0, depthUnit='in', warningLevel=0, averageDepth=2.0)

    @patch('svc.controllers.sump_controller.DeviceRepository')
    def test_save_current_level__should_call_get_device_id_by_api_key(self, mock_device, mock_sump, mock_user, mock_jwt):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, depth_info)

        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.assert_called_with(self.BEARER_TOKEN)

    @patch('svc.controllers.sump_controller.DeviceRepository')
    def test_save_current_level__should_call_insert_current_sump_level(self, mock_device, mock_sump, mock_user, mock_jwt):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_current_level(self.BEARER_TOKEN, depth_info)

        mock_sump.return_value.__enter__.return_value.insert_current_sump_level.assert_called_with(self.DEVICE_ID, depth_info)

    @patch('svc.controllers.sump_controller.DeviceRepository')
    def test_save_average_level__should_call_get_device_id_by_api_key(self, mock_device, mock_sump, mock_user, mock_jwt):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_average_level(self.BEARER_TOKEN, depth_info)

        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.assert_called_with(self.BEARER_TOKEN)

    @patch('svc.controllers.sump_controller.DeviceRepository')
    def test_save_average_level__should_call_insert_average_sump_level(self, mock_device, mock_sump, mock_user, mock_jwt):
        mock_device.return_value.__enter__.return_value.get_device_id_by_api_key.return_value = self.DEVICE_ID
        depth_info = {'depth': 'test'}

        save_average_level(self.BEARER_TOKEN, depth_info)

        mock_sump.return_value.__enter__.return_value.insert_average_sump_level.assert_called_with(self.DEVICE_ID, depth_info)
