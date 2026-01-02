import json
import os

from config.singleton import Singleton


@Singleton
class Settings:
    _settings = None

    def __init__(self):
        self.__load_settings()
        self.Queue = Queue(self._settings)
        self.Database = Database(self._settings)

    @property
    def email_app_id(self):
        return _get_setting('EMAIL_APP_ID', 'EmailAppId', self._settings)

    @property
    def weather_app_id(self):
        return _get_setting('WEATHER_APP_ID', 'WeatherAppId', self._settings)

    @property
    def jwt_secret(self):
        return _get_setting('JWT_SECRET', 'JwtSecret', self._settings)

    @property
    def light_api_key(self):
        return _get_setting('LIGHT_API_KEY', 'LightApiKey', self._settings)

    @property
    def user_id(self):
        return _get_setting('USER_ID', 'UserId', self._settings)

    @property
    def temp_file_name(self):
        return _get_setting('TEMP_FILE_NAME', 'TempFileName', self._settings)

    @property
    def allowed_origins(self):
        return self._settings.get('AllowedOrigins') if self._settings is not None else []

    def __load_settings(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(file_path, "r") as reader:
                self._settings = json.loads(reader.read())
        except Exception:
            self._settings = {}


class Database:

    def __init__(self, settings):
        self._settings = settings.get('Database') if settings is not None else None

    @property
    def user(self):
        return _get_setting('SQL_USERNAME', 'User', self._settings)

    @property
    def password(self):
        return _get_setting('SQL_PASSWORD', 'Password', self._settings)

    @property
    def name(self):
        return _get_setting('SQL_DBNAME', 'Name', self._settings)

    @property
    def port(self):
        return _get_setting('SQL_PORT', 'Port', self._settings)


class Queue:

    def __init__(self, settings):
        self._settings = settings.get('Queue') if settings is not None else None

    @property
    def user_name(self):
        return _get_setting('QUEUE_USER_NAME', 'User', self._settings)

    @property
    def password(self):
        return _get_setting('QUEUE_PASSWORD', 'Password', self._settings)

    @property
    def host(self):
        return _get_setting('QUEUE_HOST', 'Host', self._settings)

    @property
    def port(self):
        return _get_setting('QUEUE_PORT', 'Port', self._settings)

    @property
    def vhost(self):
        return _get_setting('QUEUE_VHOST', 'VHost', self._settings)


def _get_setting(env_var, setting_key, settings):
    env_var_value = os.environ.get(env_var)
    return env_var_value if env_var_value is not None else settings.get(setting_key)