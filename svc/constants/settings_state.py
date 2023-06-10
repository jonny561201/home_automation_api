import json
import os


class Settings:
    __instance = None
    settings = None
    dev_mode = False

    def __init__(self):
        if Settings.__instance is not None:
            raise Exception
        else:
            Settings.__instance = self
            Settings.__instance.__get_settings()

    @property
    def db_user(self):
        return self.settings.get('DbUser') if self.dev_mode else os.environ.get('SQL_USERNAME')

    @property
    def db_pass(self):
        return self.settings.get('DbPass') if self.dev_mode else os.environ.get('SQL_PASSWORD')

    @property
    def db_port(self):
        return self.settings.get('DbPort') if self.dev_mode else os.environ.get('SQL_PORT')

    @property
    def db_name(self):
        return self.settings.get('DbName') if self.dev_mode else os.environ.get('SQL_DBNAME')

    @property
    def email_app_id(self):
        return self.settings.get('DevEmailAppId') if self.dev_mode else os.environ.get('EMAIL_APP_ID')

    @property
    def weather_app_id(self):
        return self.settings.get('DevWeatherAppId') if self.dev_mode else os.environ.get('WEATHER_APP_ID')

    @property
    def jwt_secret(self):
        return self.settings.get('DevJwtSecret') if self.dev_mode else os.environ.get('JWT_SECRET')

    @property
    def light_api_key(self):
        return self.settings.get('lightApiKey') if self.dev_mode else os.environ.get('LIGHT_API_KEY')

    @property
    def user_id(self):
        return self.settings.get('UserId') if self.dev_mode else os.environ.get('USER_ID')

    @property
    def temp_file_name(self):
        return self.settings.get('TempFileName') if self.dev_mode else os.environ.get('TEMP_FILE_NAME')

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings.__instance = Settings()
        return Settings.__instance

    def __get_settings(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(file_path, "r") as reader:
                self.settings = json.loads(reader.read())
                self.dev_mode = self.settings.get("Development", False)
        except Exception:
            self.settings = {}
