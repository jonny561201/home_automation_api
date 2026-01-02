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
        return self._settings.get('EmailAppId') if self._settings is not None else os.environ.get('EMAIL_APP_ID')

    @property
    def weather_app_id(self):
        return self._settings.get('WeatherAppId') if self._settings is not None else os.environ.get('WEATHER_APP_ID')

    @property
    def jwt_secret(self):
        return self._settings.get('JwtSecret') if self._settings is not None else os.environ.get('JWT_SECRET')

    @property
    def light_api_key(self):
        return self._settings.get('LightApiKey') if self._settings is not None else os.environ.get('LIGHT_API_KEY')

    @property
    def user_id(self):
        return self._settings.get('UserId') if self._settings is not None else os.environ.get('USER_ID')

    @property
    def temp_file_name(self):
        return self._settings.get('TempFileName') if self._settings is not None else os.environ.get('TEMP_FILE_NAME')

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
        return os.environ.get('SQL_USERNAME') if os.environ.get('SQL_USERNAME') is not None else self._settings.get('User')

    @property
    def password(self):
        return os.environ.get('SQL_PASSWORD') if os.environ.get('SQL_PASSWORD') is not None else self._settings.get('Password')

    @property
    def name(self):
        return os.environ.get('SQL_DBNAME') if os.environ.get('SQL_DBNAME') is not None else self._settings.get('Name')

    @property
    def port(self):
        return os.environ.get('SQL_PORT') if os.environ.get('SQL_PORT') is not None else self._settings.get('Port')


class Queue:

    def __init__(self, settings):
        self._settings = settings.get('Queue') if settings is not None else None

    @property
    def user_name(self):
        return os.environ.get('QUEUE_USER_NAME') if os.environ.get('QUEUE_USER_NAME') is not None else self._settings.get('User')

    @property
    def password(self):
        return os.environ.get('QUEUE_PASSWORD') if os.environ.get('QUEUE_PASSWORD') is not None else self._settings.get('Password')

    @property
    def host(self):
        return os.environ.get('QUEUE_HOST') if os.environ.get('QUEUE_HOST') is not None else self._settings.get('Host')

    @property
    def port(self):
        return os.environ.get('QUEUE_PORT') if os.environ.get('QUEUE_PORT') is not None else self._settings.get('Port')

    @property
    def vhost(self):
        return os.environ.get('QUEUE_VHOST') if os.environ.get('QUEUE_VHOST') is not None else self._settings.get('VHost')
