import json
import os

from constants.settings_base import SettingsBase


class Settings(SettingsBase):
    __instance = None
    _settings = None

    def __init__(self):
        if Settings.__instance is not None:
            raise Exception
        else:
            Settings.__instance = self
            Settings.__instance.__load_settings()
            super().__init__(self._settings)

    @staticmethod
    def get_instance():
        if Settings.__instance is None:
            Settings.__instance = Settings()
        return Settings.__instance

    def __load_settings(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(file_path, "r") as reader:
                self._settings = json.loads(reader.read())
        except Exception:
            self._settings = {}
