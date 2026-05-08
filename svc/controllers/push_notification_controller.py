from werkzeug.exceptions import BadRequest

from svc.config.settings_state import Settings
from svc.constants.home_automation import AuthClaims
from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.push_subscription_repository import PushSubscriptionRepository
from svc.utilities.auth_utils import AuthClient
from svc.utilities.push_notification_utils import send_push_to_subscriptions


def subscribe_user(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    endpoint = request_data.get('endpoint')
    keys = request_data.get('keys', {})
    p256dh_key = keys.get('p256dh')
    auth_key = keys.get('auth')
    if endpoint is None or p256dh_key is None or auth_key is None:
        raise BadRequest()
    with PushSubscriptionRepository() as database:
        database.upsert_subscription(user_id, endpoint, p256dh_key, auth_key)


def unsubscribe_user(bearer_token, request_data):
    claims = AuthClient.get_instance().verify_jwt(bearer_token)
    user_id = claims[AuthClaims.USER_ID]
    endpoint = request_data.get('endpoint')
    if endpoint is None:
        raise BadRequest()
    with PushSubscriptionRepository() as database:
        database.delete_subscription(user_id, endpoint)


def get_vapid_public_key():
    return {'publicKey': Settings.get_instance().vapid_public_key}


def notify_household_for_device(device_id, payload):
    with DeviceRepository() as database:
        owner_id = database.get_user_id_by_device(device_id)
    if owner_id is None:
        return
    with PushSubscriptionRepository() as database:
        subscriptions = database.get_subscriptions_for_household(owner_id)
    if not subscriptions:
        return
    send_push_to_subscriptions(subscriptions, payload)
