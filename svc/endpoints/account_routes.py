import json

from flask import Blueprint, request, Response

from svc.constants.home_automation import Mime
from svc.controllers import account_controller


ACCOUNT_BLUEPRINT = Blueprint('account_routes', __name__, url_prefix='/account')


@ACCOUNT_BLUEPRINT.route('/createChildAccount', methods=['POST'])
def post_child_account_by_user():
    bearer_token = request.headers.get('Authorization')
    child_accounts = account_controller.create_child_account_by_user(bearer_token, request.get_json())
    return Response(json.dumps(child_accounts), status=200, mimetype=Mime.JSON)


@ACCOUNT_BLUEPRINT.route('/childAccounts', methods=['GET'])
def get_child_accounts():
    bearer_token = request.headers.get('Authorization')
    child_accounts = account_controller.get_child_accounts_by_user(bearer_token)
    return Response(json.dumps(child_accounts), status=200, mimetype=Mime.JSON)


@ACCOUNT_BLUEPRINT.route('/childUserId/<child_user_id>', methods=['DELETE'])
def delete_child_account(child_user_id):
    bearer_token = request.headers.get('Authorization')
    account_controller.delete_child_account(bearer_token, child_user_id)
    return Response(status=200, mimetype=Mime.JSON)
