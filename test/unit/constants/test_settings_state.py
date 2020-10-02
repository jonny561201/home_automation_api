import os

from svc.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    DB_USER = 'test_user'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER})
        self.SETTINGS = Settings.get_instance()

    def test_db_user__should_return_default_value(self):
        assert self.SETTINGS.db_user == self.DB_USER

    def test_db_user__should_pull_from_dictionary_if_dev_mode(self):
        db_user = 'other_user'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DbUser': db_user}
        assert self.SETTINGS.db_user == db_user
