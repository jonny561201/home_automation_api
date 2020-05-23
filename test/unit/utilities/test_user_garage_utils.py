from mock import patch

from svc.constants.settings_state import Settings
from svc.utilities.user_garage_utils import get_garage_url_by_user


@patch('svc.utilities.user_garage_utils.Settings')
@patch('svc.utilities.user_garage_utils.UserDatabaseManager')
class TestGarageUtils:
    USER_ID = 'heyImAUserId'

    def test_get_garage_url_by_user__should_return_localhost_url_when_dev_mode(self, mock_db, mock_settings):
        mock_settings.get_instance.return_value.get_settings.return_value = {'Development': True}
        actual = get_garage_url_by_user(self.USER_ID)

        assert actual == 'http://localhost:5001'

    def test_get_garage_url_by_user__should_call_database_when_not_dev_mode(self, mock_db, mock_settings):
        mock_settings.get_instance.return_value.get_settings.return_value = {'Development': False}
        get_garage_url_by_user(self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_user_garage_ip.assert_called_with(self.USER_ID)
