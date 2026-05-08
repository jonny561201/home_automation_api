from svc.db.repositories.device_repository import DeviceRepository
from svc.db.repositories.push_subscription_repository import PushSubscriptionRepository
from svc.utilities.push_notification_utils import send_push_to_subscriptions


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


def notify_sump_alert(device_id, alert_level):
    if alert_level != __SUMP_WARNING_LEVEL and alert_level != __SUMP_CRITICAL_LEVEL:
        return
    notify_household_for_device(device_id, __build_sump_payload(alert_level))


def __build_sump_payload(alert_level):
    if alert_level == __SUMP_CRITICAL_LEVEL:
        return {'title': 'Sump Pump Alert', 'body': 'Critical water level detected in the sump pit.', 'tag': __SUMP_ALERT_TAG, 'data': {'warningLevel': alert_level}}
    return {'title': 'Sump Pump Warning', 'body': 'Elevated water level detected in the sump pit.', 'tag': __SUMP_ALERT_TAG, 'data': {'warningLevel': alert_level}}


__SUMP_ALERT_TAG = 'sump-alert'
__SUMP_WARNING_LEVEL = 2
__SUMP_CRITICAL_LEVEL = 3
