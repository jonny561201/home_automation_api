import uuid

from svc.config.settings_state import Settings


class TestSettings:
    db_settings = {'User': 'other_user', 'Password': 'other_pass', 'Port': '1234', 'Name': 'other_name'}
    q_settings = {'Host': 'localhost', 'Port': 564, 'VHost': '/', 'User': 'guest', 'Password': 'fake+pass'}
    test_settings = {
        'EmailAppId': '098zyx',
        'WeatherAppId': '435hadsf',
        'JwtSecret': 'other_secret',
        'UserId': 'other_user_id',
        'TempFileName': 'other_file_name',
        'LightApiKey': (str(uuid.uuid4()))
    }

    def setup_method(self):
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS._settings = self.test_settings
        self.SETTINGS.Database._settings = self.db_settings
        self.SETTINGS.Queue._settings = self.q_settings

    def test_db_user__should_pull_from_file(self):
        assert self.SETTINGS.Database.user == self.db_settings['User']

    def test_db_pass__should_pull(self):
        assert self.SETTINGS.Database.password == self.db_settings['Password']

    def test_db_port__should_pull(self):
        assert self.SETTINGS.Database.port == self.db_settings['Port']

    def test_db_name__should_pull(self):
        assert self.SETTINGS.Database.name == self.db_settings['Name']

    def test_email_app_id__should_pull(self):
        assert self.SETTINGS.email_app_id == self.test_settings['EmailAppId']

    def test_weather_app_id__should_pull(self):
        assert self.SETTINGS.weather_app_id == self.test_settings['WeatherAppId']

    def test_jwt_secret__should_pull(self):
        assert self.SETTINGS.jwt_secret == self.test_settings['JwtSecret']

    def test_user_id__should_pull(self):
        assert self.SETTINGS.user_id == self.test_settings['UserId']

    def test_file_name__should_pull(self):
        assert self.SETTINGS.temp_file_name == self.test_settings['TempFileName']

    def test_light_api_key__should_pull(self):
        assert self.SETTINGS.light_api_key == self.test_settings['LightApiKey']

    def test_queue_user_name__should_pull(self):
        assert self.SETTINGS.Queue.user_name == self.q_settings['User']

    def test_queue_password__should_pull(self):
        assert self.SETTINGS.Queue.password == self.q_settings['Password']

    def test_queue_host__should_pull(self):
        assert self.SETTINGS.Queue.host == self.q_settings['Host']

    def test_queue_vhost__should_pull(self):
        assert self.SETTINGS.Queue.vhost == self.q_settings['VHost']

    def test_queue_uport__should_pull(self):
        assert self.SETTINGS.Queue.port == self.q_settings['Port']
