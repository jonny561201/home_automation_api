import uuid

from svc.constants.settings_state import Settings


class TestSettings:
    db_user = 'other_user'
    db_pass = 'other_pass'
    db_port = '1234'
    db_name = 'other_name'
    email_app_id = '098zyx'
    weather_app_id = '435hadsf'
    jwt_secret = 'other_secret'
    user_id = 'other_user_id'
    file_name = 'other_file_name'
    api_key = str(uuid.uuid4())
    q_user = 'guest'
    q_pass = 'fake+pass'
    q_port = 564
    q_host = 'localhost'
    q_vhost = '/'

    test_settings = {
        'DevEmailAppId': email_app_id,
        'DevWeatherAppId': weather_app_id,
        'DevJwtSecret': jwt_secret,
        'UserId': user_id,
        'TempFileName': file_name,
        'lightApiKey': api_key,
        'Database' : {'User': db_user,'Pass': db_pass,'Port': db_port, 'Name': db_name},
        'Queue': {'Host': q_host,'Port': q_port,'VHost': q_vhost,'User': q_user,'Password': q_pass}
    }
    SETTINGS = Settings.get_instance(True, test_settings)

    def test_db_user__should_pull_from_file_if_test_mode(self):
        assert self.SETTINGS.Database.user == self.db_user

    def test_db_pass__should_pull_if_test_mode(self):
        assert self.SETTINGS.Database.password == self.db_pass

    def test_db_port__should_pull_if_test_mode(self):
        assert self.SETTINGS.Database.port == self.db_port

    def test_db_name__should_pull_if_test_mode(self):
        assert self.SETTINGS.Database.name == self.db_name

    def test_email_app_id__should_pull_if_test_mode(self):
        assert self.SETTINGS.email_app_id == self.email_app_id

    def test_weather_app_id__should_pull_if_test_mode(self):
        assert self.SETTINGS.weather_app_id == self.weather_app_id

    def test_jwt_secret__should_pull_if_test_mode(self):
        assert self.SETTINGS.jwt_secret == self.jwt_secret

    def test_user_id__should_pull_if_test_mode(self):
        assert self.SETTINGS.user_id == self.user_id

    def test_file_name__should_pull_if_test_mode(self):
        assert self.SETTINGS.temp_file_name == self.file_name

    def test_light_api_key__should_pull_if_test_mode(self):
        assert self.SETTINGS.light_api_key == self.api_key

    def test_queue_user_name__should_pull_if_test_mode(self):
        assert self.SETTINGS.Queue.user_name == self.q_user

    def test_queue_password__should_pull_if_test_mode(self):
        assert self.SETTINGS.Queue.password == self.q_pass

    def test_queue_host__should_pull_if_test_mode(self):
        assert self.SETTINGS.Queue.host == self.q_host

    def test_queue_vhost__should_pull_if_test_mode(self):
        assert self.SETTINGS.Queue.vhost == self.q_vhost

    def test_queue_uport__should_pull_if_test_mode(self):
        assert self.SETTINGS.Queue.port == self.q_port
