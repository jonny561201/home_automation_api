import json

from flask import Blueprint, request, Response

from svc.controllers import account_controller

ACCOUNT_BLUEPRINT = Blueprint('account_routes', __name__, url_prefix='/account')
DEFAULT_HEADERS = {'Content-Type': 'text/json'}


@ACCOUNT_BLUEPRINT.route('/userId/<user_id>/updateAccount', methods=['POST'])
def update_user_password(user_id):
    bearer_token = request.headers.get('Authorization')
    account_controller.change_password(bearer_token, user_id,  request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)


@ACCOUNT_BLUEPRINT.route('/userId/<user_id>/createChildAccount', methods=['POST'])
def post_child_account_by_user(user_id):
    bearer_token = request.headers.get('Authorization')
    account_controller.create_child_account_by_user(bearer_token, user_id, request.data)
    return Response(status=200, headers=DEFAULT_HEADERS)


@ACCOUNT_BLUEPRINT.route('/userId/<user_id>/childAccounts', methods=['GET'])
def get_child_accounts_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    child_accounts = account_controller.get_child_accounts_by_user(bearer_token, user_id)
    return Response(json.dumps(child_accounts), status=200, headers=DEFAULT_HEADERS)


@ACCOUNT_BLUEPRINT.route('/userId/<user_id>/roles', methods=['GET'])
def get_roles_by_user_id(user_id):
    bearer_token = request.headers.get('Authorization')
    roles = account_controller.get_roles(bearer_token, user_id)
    return Response(json.dumps(roles), status=200, headers=DEFAULT_HEADERS)


def delete_child_account_by_user_id(user_id, child_user_id):
    bearer_token = request.headers['Authorization']
    account_controller.delete_child_account(bearer_token, user_id, child_user_id)