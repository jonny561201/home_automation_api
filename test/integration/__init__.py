from config.settings_state import Settings

settings = {'User': 'postgres', 'Password': 'password', 'Name': 'garage_door', 'Port': '5432'}
Settings.get_instance().Database._settings = settings