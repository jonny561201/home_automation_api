import os
import uuid

from svc.config.settings_state import Settings


class TestSettingsEnvVars:
    ENV_VARS = {'SQL_USERNAME': 'test_user', 'SQL_PASSWORD': 'test_pass', 'SQL_PORT': '5231',
                'SQL_DBNAME': 'fake_name', 'EMAIL_APP_ID': 'abc123', 'WEATHER_APP_ID': '345def',
                'JWT_SECRET': 'FakeSecret', 'TEMP_FILE_NAME': 'test.json', 'USER_ID': 'sdf234',
                'LIGHT_API_KEY': str(uuid.uuid4()), 'QUEUE_USER_NAME': 'queue_user', 'QUEUE_PASSWORD': 'queue_pass',
                'QUEUE_HOST': 'localhost', 'QUEUE_PORT': '5642', 'QUEUE_VHOST': 'vhost'
                }

    def setup_method(self):
        os.environ.update(self.ENV_VARS)
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS._settings = None
        self.SETTINGS.Database._settings = None
        self.SETTINGS.Queue._settings = None

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
        assert self.SETTINGS.Database.user == self.ENV_VARS['SQL_USERNAME']

    def test_db_pass__should_return_value(self):
        assert self.SETTINGS.Database.password == self.ENV_VARS['SQL_PASSWORD']

    def test_db_port__should_return_value(self):
        assert self.SETTINGS.Database.port == self.ENV_VARS['SQL_PORT']

    def test_db_name__should_return_value(self):
        assert self.SETTINGS.Database.name == self.ENV_VARS['SQL_DBNAME']

    def test_email_app_id__should_return_value(self):
        assert self.SETTINGS.email_app_id == self.ENV_VARS['EMAIL_APP_ID']

    def test_weather_app_id__should_return_value(self):
        assert self.SETTINGS.weather_app_id == self.ENV_VARS['WEATHER_APP_ID']

    def test_jwt_secret__should_return_value(self):
        assert self.SETTINGS.jwt_secret == self.ENV_VARS['JWT_SECRET']

    def test_user_id__should_return_value(self):
        assert self.SETTINGS.user_id == self.ENV_VARS['USER_ID']

    def test_file_name__should_return_value(self):
        assert self.SETTINGS.temp_file_name == self.ENV_VARS['TEMP_FILE_NAME']

    def test_light_api_key__should_return_value(self):
        assert self.SETTINGS.light_api_key == self.ENV_VARS['LIGHT_API_KEY']

    def test_queue_user_name__should_return_value(self):
        assert self.SETTINGS.Queue.user_name == self.ENV_VARS['QUEUE_USER_NAME']

    def test_queue_password__should_return_value(self):
        assert self.SETTINGS.Queue.password == self.ENV_VARS['QUEUE_PASSWORD']

    def test_queue_host__should_return_value(self):
        assert self.SETTINGS.Queue.host == self.ENV_VARS['QUEUE_HOST']

    def test_queue_vhost__should_return_value(self):
        assert self.SETTINGS.Queue.vhost == self.ENV_VARS['QUEUE_VHOST']

    def test_queue_port__should_return_value(self):
        assert self.SETTINGS.Queue.port == self.ENV_VARS['QUEUE_PORT']
