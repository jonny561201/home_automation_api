import json

import pytest
from flask import Flask
from mock import patch, ANY
from werkzeug.exceptions import Unauthorized

from svc.endpoints.account_routes import post_child_account_by_user, get_child_accounts, delete_child_account
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.account_routes.account_controller')
class TestChildAccountRoutes:
    USER_ID = '123bac34'
    FAKE_JWT_TOKEN = 'fakeJwtToken'
    HEADERS = {'Authorization': FAKE_JWT_TOKEN}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, headers=self.HEADERS)

    def teardown_method(self):
        self.ctx.pop()

    def test_delete_child_account__should_call_controller_with_bearer_token(self, mock_controller):
        child_user_id = '123abc'
        delete_child_account(child_user_id)

        mock_controller.delete_child_account.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_delete_child_account__should_call_controller_with_child_user_id(self, mock_controller):
        child_user_id = '123abc'
        delete_child_account(child_user_id)

        mock_controller.delete_child_account.assert_called_with(ANY, child_user_id)

    def test_delete_child_account__should_not_raise_error_when_trying_to_get_bearer_token(self, mock_controller):
        child_user_id = '123abc'
        delete_child_account(child_user_id)

        mock_controller.delete_child_account.assert_called()

    def test_delete_child_account__should_return_success_status_code(self, mock_controller):
        child_user_id = '123abc'
        actual = delete_child_account(child_user_id)

        assert actual.status_code == 200

    def test_delete_child_account__should_return_default_headers(self, mock_controller):
        child_user_id = '123abc'
        actual = delete_child_account(child_user_id)

        assert actual.content_type == 'application/json'

    def test_post_child_account_by_user__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.create_child_account_by_user.return_value = {}
        post_child_account_by_user()
        mock_controller.create_child_account_by_user.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_post_child_account_by_user__not_raise_error_when_no_authorization_header(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx)
        mock_controller.create_child_account_by_user.return_value = {}
        post_child_account_by_user()
        mock_controller.create_child_account_by_user.assert_called_with(None, ANY)

    def test_post_child_account_by_user__should_call_controller_with_post_body(self, mock_controller):
        request_data = {'fake': 'request'}
        self.ctx = setup_request(self.app, self.ctx, request_data)
        mock_controller.create_child_account_by_user.return_value = {}
        post_child_account_by_user()
        mock_controller.create_child_account_by_user.assert_called_with(ANY, request_data)

    def test_post_child_account_by_user__should_return_success_status_code(self, mock_controller):
        mock_controller.create_child_account_by_user.return_value = {}
        actual = post_child_account_by_user()
        assert actual.status_code == 200

    def test_post_child_account_by_user__should_return_success_headers(self, mock_controller):
        mock_controller.create_child_account_by_user.return_value = {}
        actual = post_child_account_by_user()
        assert actual.content_type == 'application/json'

    def test_post_child_account_by_user__should_return_controller_response(self, mock_controller):
        response = {'test': 'fake data'}
        mock_controller.create_child_account_by_user.return_value = response
        actual = post_child_account_by_user()
        assert json.loads(actual.data) == response

    def test_get_child_accounts__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_child_accounts_by_user.return_value = {}
        get_child_accounts()
        mock_controller.get_child_accounts_by_user.assert_called_with(self.FAKE_JWT_TOKEN)

    def test_get_child_accounts__should_return_success_status_code(self, mock_controller):
        mock_controller.get_child_accounts_by_user.return_value = {}
        actual = get_child_accounts()
        assert actual.status_code == 200

    def test_get_child_accounts__should_return_success_headers(self, mock_controller):
        mock_controller.get_child_accounts_by_user.return_value = {}
        actual = get_child_accounts()
        assert actual.content_type == 'application/json'

    def test_get_child_accounts__should_return_response_from_controller(self, mock_controller):
        response = {'test': 'test data'}
        mock_controller.get_child_accounts_by_user.return_value = response
        actual = get_child_accounts()

        assert json.loads(actual.data) == response

    def test_get_child_accounts__should_not_throw_exception_when_no_bearer_token(self, mock_controller):
        mock_controller.get_child_accounts_by_user.side_effect = Unauthorized()
        with pytest.raises(Unauthorized):
            get_child_accounts()
