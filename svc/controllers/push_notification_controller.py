from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.db.repositories.push_subscription_repository import PushSubscriptionRepository
from svc.utilities.auth_utils import AuthClient


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
