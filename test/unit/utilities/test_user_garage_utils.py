from mock import patch

from svc.constants.settings_state import Settings
from svc.utilities.user_garage_utils import get_garage_url_by_user


@patch('svc.utilities.user_garage_utils.UserDatabaseManager')
class TestGarageUtils:
    USER_ID = 'heyImAUserId'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True

    def test_get_garage_url_by_user__should_return_localhost_url_when_dev_mode(self, mock_db):
        actual = get_garage_url_by_user(self.USER_ID)

        assert actual == 'http://localhost:5001'

    def test_get_garage_url_by_user__should_call_database_when_settings_cannot_be_found(self, mock_db):
        self.SETTINGS.dev_mode = False
        get_garage_url_by_user(self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_user_garage_ip.assert_called_with(self.USER_ID)

    def test_get_garage_url_by_user__should_return_url_with_ip_from_database(self, mock_db):
        database_response = '1.1.1.1'
        self.SETTINGS.dev_mode = False
        mock_db.return_value.__enter__.return_value.get_user_garage_ip.return_value = database_response
        actual = get_garage_url_by_user(self.USER_ID)

        assert actual == f'http://{database_response}'

