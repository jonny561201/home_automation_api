from svc.config.settings_state import Settings

settings = {'User': 'postgres', 'Password': 'password', 'Name': 'garage_door', 'Port': '5432', 'Host': 'localhost'}
Settings.get_instance().Database._settings = settings