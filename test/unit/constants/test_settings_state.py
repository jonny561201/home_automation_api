import os

from svc.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    DB_USER = 'test_user'
    DB_PASS = 'test_pass'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS})
        self.SETTINGS = Settings.get_instance()

    def teardown_method(self):
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')

    def test_db_user__should_return_env_var_value(self):
        assert self.SETTINGS.db_user == self.DB_USER

    def test_db_pass__should_return_env_var_value(self):
        assert self.SETTINGS.db_pass == self.DB_PASS

    def test_db_user__should_pull_from_dictionary_if_dev_mode(self):
        db_user = 'other_user'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DbUser': db_user}
        assert self.SETTINGS.db_user == db_user

    def test_db_pass__should_pull_from_dictionary_if_dev_mode(self):
        db_pass = 'other_pass'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DbPass': db_pass}
        assert self.SETTINGS.db_pass == db_pass

