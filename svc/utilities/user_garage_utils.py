from svc.db.methods.user_credentials import UserDatabaseManager


def get_garage_url_by_user(user_id):
    with UserDatabaseManager() as database:
        ip = database.get_user_garage_ip(user_id)
        return f'http://{ip}'
