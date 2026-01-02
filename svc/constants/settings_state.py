import json
import os

from constants.settings_base import SettingsBase
from constants.singleton import Singleton


@Singleton
class Settings(SettingsBase):
    _settings = None

    def __init__(self):
        super().__init__(self._settings)

    def __load_settings(self):
        try:
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            with open(file_path, "r") as reader:
                self._settings = json.loads(reader.read())
        except Exception:
            self._settings = {}
