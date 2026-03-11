from svc.models.garage import GarageState
from svc.constants.home_automation import Automation
from svc.utilities import api_utils
from svc.utilities.jwt_utils import is_jwt_valid
from svc.utilities.user_garage_utils import get_garage_url_by_user
from svc.utilities.rabbitmq_client import publish


def get_status(bearer_token, user_id, garage_id):
    is_jwt_valid(bearer_token)
    base_url = get_garage_url_by_user(user_id)

    return api_utils.get_garage_door_status(bearer_token, base_url, garage_id)


def update_state(bearer_token, user_id, garage_id, request):
    is_jwt_valid(bearer_token)
    message = {'id': garage_id, 'action': 'update', 'open': request['garageDoorOpen']}
    publish(Automation.GARAGE.QUEUE, message)

    return GarageState(isGarageOpen=request['garageDoorOpen'])


def toggle_door(bearer_token, user_id, garage_id):
    is_jwt_valid(bearer_token)
    message = {'id': garage_id, 'action': 'toggle'}

    publish(Automation.GARAGE.QUEUE, message)
