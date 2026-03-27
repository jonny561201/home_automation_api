from werkzeug.exceptions import BadRequest, Unauthorized

from svc.config.settings_state import Settings
from svc.db.repositories.account_repository import AccountRepository
from svc.utilities import api_utils


def exchange_auth_code(request_data):
    code = request_data.get('code')
    code_verifier = request_data.get('code_verifier')
    redirect_uri = request_data.get('redirect_uri')

    if not code or not code_verifier or not redirect_uri:
        raise BadRequest()

    return api_utils.exchange_auth0_code(code, code_verifier, redirect_uri)


def provision_user(api_key, request_data):
    settings = Settings.get_instance()
    if not api_key or api_key != settings.Authority.provision_api_key:
        raise Unauthorized()
    first_name = request_data.get('first_name')
    last_name = request_data.get('last_name')
    email = request_data.get('email')
    if not first_name or not last_name or not email:
        raise BadRequest()
    with AccountRepository() as database:
        return database.provision_user(first_name, last_name, email)
