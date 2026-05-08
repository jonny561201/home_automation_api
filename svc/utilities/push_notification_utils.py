import json
import logging

from pywebpush import WebPushException, webpush

from svc.config.settings_state import Settings
from svc.db.repositories.push_subscription_repository import PushSubscriptionRepository


def send_push_to_subscriptions(subscriptions, payload):
    settings = Settings.get_instance()
    private_key = settings.vapid_private_key
    claims = {'sub': settings.vapid_subject}
    body = json.dumps(payload)
    for subscription in subscriptions:
        __send_or_cleanup(subscription, body, private_key, claims)


def __send_or_cleanup(subscription, body, private_key, claims):
    info = {'endpoint': subscription.endpoint, 'keys': {'p256dh': subscription.p256dh_key, 'auth': subscription.auth_key}}
    try:
        webpush(subscription_info=info, data=body, vapid_private_key=private_key, vapid_claims=dict(claims))
    except WebPushException as exc:
        status = exc.response.status_code if exc.response is not None else None
        if status == 404 or status == 410:
            with PushSubscriptionRepository() as database:
                database.delete_subscription_by_endpoint(subscription.endpoint)
            return
        logging.warning(f'Failed to deliver push notification: {str(exc)}')
