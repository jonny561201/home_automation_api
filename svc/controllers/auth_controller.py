from werkzeug.exceptions import BadRequest

from svc.utilities import api_utils


def exchange_auth_code(request_data):
    code = request_data.get('code')
    code_verifier = request_data.get('code_verifier')
    redirect_uri = request_data.get('redirect_uri')

    if not code or not code_verifier or not redirect_uri:
        raise BadRequest()

    return api_utils.exchange_auth0_code(code, code_verifier, redirect_uri)
