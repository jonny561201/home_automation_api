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
    def light_api_user(self):
        return self.settings.get('LightApiUser') if self.dev_mode else os.environ.get('LIGHT_API_USERNAME')

    @property
    def light_api_password(self):
        return self.settings.get('LightApiPass') if self.dev_mode else os.environ.get('LIGHT_API_PASSWORD')

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings.__instance = Settings()
        return Settings.__instance

    def __get_settings(self):
        try:
            with open("./settings.json", "r") as reader:
                self.settings = json.loads(reader.read())
                self.dev_mode = self.settings.get("Development", False)
        except FileNotFoundError:
            self.settings = {}
