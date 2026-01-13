from svc.db.methods.device_repository import DeviceRepository


def get_garage_url_by_user(user_id):
    with DeviceRepository() as database:
        ip = database.get_user_garage_ip(user_id)
        return f'http://{ip}'
