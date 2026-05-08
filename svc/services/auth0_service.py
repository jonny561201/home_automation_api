from svc.utilities import api_utils


def provision_account(email, role_ids):
    auth0_user_id = api_utils.create_auth0_user(email)
    if role_ids:
        api_utils.assign_auth0_roles(auth0_user_id, role_ids)
    api_utils.send_auth0_password_reset(email)


def assign_roles(auth0_id, role_ids):
    if role_ids:
        api_utils.assign_auth0_roles(auth0_id, role_ids)
