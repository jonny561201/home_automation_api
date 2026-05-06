from werkzeug.exceptions import BadRequest

from svc.utilities.api_utils import get_census_reverse_geocode
from svc.utilities.auth_utils import AuthClient


def reverse_geocode(bearer_token, latitude, longitude):
    AuthClient.get_instance().verify_jwt(bearer_token)
    if latitude is None or longitude is None:
        raise BadRequest()

    response = get_census_reverse_geocode(latitude, longitude)
    geographies = response.get('result', {}).get('geographies', {})
    states = geographies.get('States', [])
    if len(states) == 0:
        return {}

    state = states[0].get('STUSAB')
    city = __resolve_city(geographies)
    if state is None or city is None:
        return {}
    return {'city': city, 'state': state}


def __resolve_city(geographies):
    for key in ['Incorporated Places', 'Census Designated Places', 'Counties']:
        entries = geographies.get(key, [])
        if len(entries) == 0:
            continue
        base_name = entries[0].get('BASENAME')
        if base_name is not None:
            return base_name
    return None
