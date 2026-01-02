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
        return self._settings.get('DevEmailAppId') if self._settings is not None else os.environ.get('EMAIL_APP_ID')

    @property
    def weather_app_id(self):
        return self._settings.get('DevWeatherAppId') if self._settings is not None else os.environ.get('WEATHER_APP_ID')

    @property
    def jwt_secret(self):
        return self._settings.get('DevJwtSecret') if self._settings is not None else os.environ.get('JWT_SECRET')

    @property
    def light_api_key(self):
        return self._settings.get('lightApiKey') if self._settings is not None else os.environ.get('LIGHT_API_KEY')

    @property
    def user_id(self):
        return self._settings.get('UserId') if self._settings is not None else os.environ.get('USER_ID')

    @property
    def temp_file_name(self):
        return self._settings.get('TempFileName') if self._settings is not None else os.environ.get('TEMP_FILE_NAME')

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
        return self._settings.get('User') if self._settings is not None else os.environ.get('SQL_USERNAME')

    @property
    def password(self):
        return self._settings.get('Password') if self._settings is not None else os.environ.get('SQL_PASSWORD')

    @property
    def name(self):
        return self._settings.get('Name') if self._settings is not None else os.environ.get('SQL_DBNAME')

    @property
    def port(self):
        return self._settings.get('Port') if self._settings is not None else os.environ.get('SQL_PORT')


class Queue:

    def __init__(self, settings):
        self._settings = settings.get('Queue') if settings is not None else None

    @property
    def user_name(self):
        return self._settings.get('User') if self._settings is not None else os.environ.get('QUEUE_USER_NAME')

    @property
    def password(self):
        return self._settings.get('Password') if self._settings is not None else os.environ.get('QUEUE_PASSWORD')

    @property
    def host(self):
        return self._settings.get('Host') if self._settings is not None else os.environ.get('QUEUE_HOST')

    @property
    def port(self):
        return self._settings.get('Port') if self._settings is not None else os.environ.get('QUEUE_PORT')

    @property
    def vhost(self):
        return self._settings.get('VHost') if self._settings is not None else os.environ.get('QUEUE_VHOST')
