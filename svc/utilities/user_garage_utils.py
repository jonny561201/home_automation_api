from svc.constants.settings_state import Settings
from svc.db.methods.user_credentials import UserDatabaseManager


def get_garage_url_by_user(user_id):
    settings = Settings.get_instance()
    if settings.dev_mode:
        return 'http://localhost:5001'
    with UserDatabaseManager() as database:
        ip = database.get_user_garage_ip(user_id)
        return 'http://%s:5001' % ip
