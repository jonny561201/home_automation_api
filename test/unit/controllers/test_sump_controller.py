from datetime import datetime, date
from decimal import Decimal

from mock import patch, MagicMock

from svc.constants.home_automation import AuthClaims
from svc.models.app import Preference
from svc.models.sump import SumpLevel, SumpReading, SumpReadings, SumpDailyReading, SumpDailyReadings
from svc.controllers.sump_controller import get_sump_level, get_depth_history, get_daily_averages, save_current_level, save_average_level


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


@patch('svc.controllers.sump_controller.AuthClient')
@patch('svc.controllers.sump_controller.SumpRepository')
class TestSumpHistoryController:
    USER_ID = 'fake1234'
    DEVICE_ID = 'device5678'
    CLAIMS = {AuthClaims.USER_ID: USER_ID}
    BEARER_TOKEN = 'lkhasdhlufiou0892390784'

    def test_get_depth_history__should_validate_jwt(self, mock_sump, mock_jwt):
        get_depth_history(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_depth_history__should_return_todays_readings(self, mock_sump, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        ts = datetime(2026, 4, 21, 14, 30, 0)
        reading = MagicMock(distance=Decimal('11.2'), create_date=ts)
        mock_sump.return_value.__enter__.return_value.get_daily_readings_by_device.return_value = [reading]

        actual = get_depth_history(self.BEARER_TOKEN)

        assert actual == SumpReadings(readings=[SumpReading(depth=11.2, dateTime=ts)])

    def test_get_depth_history__should_return_empty_when_no_readings(self, mock_sump, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_daily_readings_by_device.return_value = []

        actual = get_depth_history(self.BEARER_TOKEN)

        assert actual == SumpReadings(readings=[])

    def test_get_daily_averages__should_validate_jwt(self, mock_sump, mock_jwt):
        get_daily_averages(self.BEARER_TOKEN, 7)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_daily_averages__should_pass_days_to_repository(self, mock_sump, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        mock_sump.return_value.__enter__.return_value.get_average_readings_by_device.return_value = []

        get_daily_averages(self.BEARER_TOKEN, 30)

        mock_sump.return_value.__enter__.return_value.get_average_readings_by_device.assert_called_with(self.DEVICE_ID, 30)

    def test_get_daily_averages__should_return_readings(self, mock_sump, mock_jwt):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = self.CLAIMS
        mock_sump.return_value.__enter__.return_value.get_sump_device_id_by_user.return_value = self.DEVICE_ID
        day = date(2026, 4, 15)
        reading = MagicMock(distance=Decimal('12.1'), create_day=day)
        mock_sump.return_value.__enter__.return_value.get_average_readings_by_device.return_value = [reading]

        actual = get_daily_averages(self.BEARER_TOKEN, 7)

        assert actual == SumpDailyReadings(readings=[SumpDailyReading(depth=12.1, date=day)])
