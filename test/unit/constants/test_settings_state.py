import os

from svc.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    DB_USER = 'test_user'
    DB_PASS = 'test_pass'
    DB_NAME = 'fake_name'
    DB_PORT = '5231'

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS, 'SQL_PORT': self.DB_PORT,
                           'SQL_DBNAME': self.DB_NAME})
        self.SETTINGS = Settings.get_instance()

    def teardown_method(self):
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('SQL_PORT')
        os.environ.pop('SQL_DBNAME')

    def test_db_user__should_return_env_var_value(self):
        assert self.SETTINGS.db_user == self.DB_USER

    def test_db_pass__should_return_env_var_value(self):
        assert self.SETTINGS.db_pass == self.DB_PASS

    def test_db_port__should_return_env_var_value(self):
        assert self.SETTINGS.db_port == self.DB_PORT

    def test_db_name__should_return_env_var_value(self):
        assert self.SETTINGS.db_name == self.DB_NAME

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

    def test_db_port__should_pull_from_dictionary_if_dev_mode(self):
        db_port = '1234'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DbPort': db_port}
        assert self.SETTINGS.db_port == db_port

    def test_db_name__should_pull_from_dictionary_if_dev_mode(self):
        db_name = 'other_name'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DbName': db_name}
        assert self.SETTINGS.db_name == db_name

