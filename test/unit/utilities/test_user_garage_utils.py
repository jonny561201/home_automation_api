from svc.constants.settings_state import Settings
from svc.utilities.user_garage_utils import get_garage_url_by_user


class TestGarageUtils:
    USER_ID = 'heyImAUserId'

    def setup_method(self):
        self.SETTINGS = Settings.get_instance().get_settings()

    def test_get_garage_url_by_user__should_return_localhost_url_when_dev_mode(self):
        self.SETTINGS['Development'] = True
        actual = get_garage_url_by_user(self.USER_ID)

        assert actual == 'http://localhost:5001'
