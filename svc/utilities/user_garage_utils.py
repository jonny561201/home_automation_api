from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager


def get_garage_url_by_user(user_id):
    settings = Settings.get_instance().get_settings()
    if settings['Development']:
        return 'http://localhost:5001'
    with UserDatabaseManager() as database:
        database.get_user_garage_ip(user_id)

    # TODO: get ip address from the database!!!  if in testing mode use local host
    # return 'http://192.168.1.175:5001'
