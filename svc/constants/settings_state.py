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

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings.__instance = Settings()
        return Settings.__instance

    def get_settings(self):
        if self.settings is None:
            try:
                with open("./settings.json", "r") as reader:
                    self.settings = json.loads(reader.read())
                    self.dev_mode = ["Development"]
                return self.settings
            except FileNotFoundError:
                return {}
        else:
            return self.settings
