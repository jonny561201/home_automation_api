import os
import uuid

from constants.settings_state import Settings


class TestSettingsEnvVars:
    USER_ID = 'sdf234'
    DB_PORT = '5231'
    DB_USER = 'test_user'
    DB_PASS = 'test_pass'
    DB_NAME = 'fake_name'
    EMAIL_APP_ID = 'abc123'
    FILE_NAME = 'test.json'
    WEATHER_APP_ID = '345def'
    JWT_SECRET = 'FakeSecret'
    LIGHT_API_KEY = str(uuid.uuid4())
    Q_USER = 'queue_user'
    Q_PASS = 'queue_pass'
    Q_HOST = 'localhost'
    Q_PORT = '5642'
    Q_VHOST = 'vhost'
    SETTINGS = None

    def setup_method(self):
        os.environ.update({'SQL_USERNAME': self.DB_USER, 'SQL_PASSWORD': self.DB_PASS, 'SQL_PORT': self.DB_PORT,
                           'SQL_DBNAME': self.DB_NAME, 'EMAIL_APP_ID': self.EMAIL_APP_ID, 'WEATHER_APP_ID': self.WEATHER_APP_ID,
                           'JWT_SECRET': self.JWT_SECRET, 'TEMP_FILE_NAME': self.FILE_NAME, 'USER_ID': self.USER_ID,
                           'LIGHT_API_KEY': self.LIGHT_API_KEY, 'QUEUE_USER_NAME': self.Q_USER, 'QUEUE_PASSWORD': self.Q_PASS,
                           'QUEUE_HOST': self.Q_HOST, 'QUEUE_PORT': self.Q_PORT, 'QUEUE_VHOST': self.Q_VHOST
        })
        self.SETTINGS = Settings.get_instance(True)

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
        os.environ.pop('QUEUE_USER_NAME')
        os.environ.pop('QUEUE_PASSWORD')
        os.environ.pop('QUEUE_HOST')
        os.environ.pop('QUEUE_PORT')
        os.environ.pop('QUEUE_VHOST')

    def test_db_user__should_return_value(self):
        assert self.SETTINGS.Database.user == self.DB_USER

    def test_db_pass__should_return_value(self):
        assert self.SETTINGS.Database.password == self.DB_PASS

    def test_db_port__should_return_value(self):
        assert self.SETTINGS.Database.port == self.DB_PORT

    def test_db_name__should_return_value(self):
        assert self.SETTINGS.Database.name == self.DB_NAME

    def test_email_app_id__should_return_value(self):
        assert self.SETTINGS.email_app_id == self.EMAIL_APP_ID

    def test_weather_app_id__should_return_value(self):
        assert self.SETTINGS.weather_app_id == self.WEATHER_APP_ID

    def test_jwt_secret__should_return_value(self):
        assert self.SETTINGS.jwt_secret == self.JWT_SECRET

    def test_user_id__should_return_value(self):
        assert self.SETTINGS.user_id == self.USER_ID

    def test_file_name__should_return_value(self):
        assert self.SETTINGS.temp_file_name == self.FILE_NAME

    def test_light_api_key__should_return_value(self):
        assert self.SETTINGS.light_api_key == self.LIGHT_API_KEY

    def test_queue_user_name__should_return_value(self):
        assert self.SETTINGS.Queue.user_name == self.Q_USER

    def test_queue_password__should_return_value(self):
        assert self.SETTINGS.Queue.password == self.Q_PASS

    def test_queue_host__should_return_value(self):
        assert self.SETTINGS.Queue.host == self.Q_HOST

    def test_queue_vhost__should_return_value(self):
        assert self.SETTINGS.Queue.vhost == self.Q_VHOST

    def test_queue_port__should_return_value(self):
        assert self.SETTINGS.Queue.port == self.Q_PORT
