import os
import uuid

from svc.constants.settings_state import Settings


class TestState:
    SETTINGS = None
    USER_ID = 'sdf234'
    DB_PORT = '5231'
    DB_USER = 'test_user'
    DB_PASS = 'test_pass'
    DB_NAME = 'fake_name'
    EMAIL_APP_ID = 'abc123'
    FILE_NAME = "test.json"
    WEATHER_APP_ID = '345def'
    JWT_SECRET = 'FakeSecret'
    LIGHT_API_KEY = str(uuid.uuid4())

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS, 'SQL_PORT': self.DB_PORT,
                           'SQL_DBNAME': self.DB_NAME, 'EMAIL_APP_ID': self.EMAIL_APP_ID, 'WEATHER_APP_ID': self.WEATHER_APP_ID,
                           'JWT_SECRET': self.JWT_SECRET, 'TEMP_FILE_NAME': self.FILE_NAME, 'USER_ID': self.USER_ID,
                           'LIGHT_API_KEY': self.LIGHT_API_KEY})
        self.SETTINGS = Settings.get_instance()

    def teardown_method(self):
        os.environ.pop('USER_ID')
        os.environ.pop('SQL_PORT')
        os.environ.pop('TEMP_FILE_NAME')
        os.environ.pop('JWT_SECRET')
        os.environ.pop('SQL_DBNAME')
        os.environ.pop('SQL_USERNAME')
        os.environ.pop('SQL_PASSWORD')
        os.environ.pop('EMAIL_APP_ID')
        os.environ.pop('WEATHER_APP_ID')
        os.environ.pop('LIGHT_API_KEY')

    def test_db_user__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.db_user == self.DB_USER

    def test_db_pass__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.db_pass == self.DB_PASS

    def test_db_port__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.db_port == self.DB_PORT

    def test_db_name__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.db_name == self.DB_NAME

    def test_email_app_id__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.email_app_id == self.EMAIL_APP_ID

    def test_weather_app_id__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.weather_app_id == self.WEATHER_APP_ID

    def test_jwt_secret__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.jwt_secret == self.JWT_SECRET

    def test_user_id__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.user_id == self.USER_ID

    def test_file_name__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.temp_file_name == self.FILE_NAME

    def test_light_api_key__should_return_env_var_value(self):
        self.SETTINGS.dev_mode = False
        assert self.SETTINGS.light_api_key == self.LIGHT_API_KEY

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

    def test_email_app_id__should_pull_from_dictionary_if_dev_mode(self):
        email_app_id = '098zyx'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DevEmailAppId': email_app_id}
        assert self.SETTINGS.email_app_id == email_app_id

    def test_weather_app_id__should_pull_from_dictionary_if_dev_mode(self):
        weather_app_id = '435hadsf'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DevWeatherAppId': weather_app_id}
        assert self.SETTINGS.weather_app_id == weather_app_id

    def test_jwt_secret__should_pull_from_dictionary_if_dev_mode(self):
        jwt_secret = 'other_secret'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'DevJwtSecret': jwt_secret}
        assert self.SETTINGS.jwt_secret == jwt_secret

    def test_user_id__should_pull_from_dictionary_if_dev_mode(self):
        user_id = 'other_user_id'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'UserId': user_id}
        assert self.SETTINGS.user_id == user_id

    def test_file_name__should_pull_from_dictionary_if_dev_mode(self):
        file_name = 'other_file_name'
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'TempFileName': file_name}
        assert self.SETTINGS.temp_file_name == file_name

    def test_light_api_key__should_pull_from_dictionary_if_dev_mode(self):
        api_key = str(uuid.uuid4())
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'lightApiKey': api_key}
        assert self.SETTINGS.light_api_key == api_key
