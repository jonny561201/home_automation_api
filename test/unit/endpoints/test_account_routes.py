import json

import pytest
from flask import Flask
from mock import patch, ANY
from werkzeug.exceptions import Unauthorized

from svc.endpoints.account_routes import update_user_password, post_child_account_by_user, get_child_accounts, \
    get_roles, get_roles_v2, delete_child_account
from test.unit.test_helpers import setup_request


@patch('svc.endpoints.account_routes.account_controller')
class TestAppRoutes:
    USER_ID = '123bac34'
    FAKE_JWT_TOKEN = 'fakeJwtToken'
    REQUEST = {'fakeData': 'doesnt matter'}

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, bearer=self.FAKE_JWT_TOKEN)

    def teardown_method(self):
        self.ctx.pop()

    def test_update_user_password__should_call_change_password_controller_with_bearer_token(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx, self.REQUEST, self.FAKE_JWT_TOKEN)
        update_user_password()

        mock_controller.change_password.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_update_user_password__should_call_change_password_controller_with_data(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx, self.REQUEST)
        update_user_password()

        mock_controller.change_password.assert_called_with(ANY, self.REQUEST)

    def test_update_user_password__should_return_success_status_code(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx, self.REQUEST)
        actual = update_user_password()

        assert actual.status_code == 200

    def test_update_user_password__should_return_success_content(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx, self.REQUEST)
        actual = update_user_password()

        assert actual.content_type == 'application/json'

    def test_get_roles__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_roles.return_value = {}
        get_roles()

        mock_controller.get_roles.assert_called_with(self.FAKE_JWT_TOKEN)

    def test_get_roles__should_not_throw_exception_when_no_header(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx)
        mock_controller.get_roles.return_value = {}
        get_roles()

        mock_controller.get_roles.assert_called_with(None)

    def test_get_roles__should_return_success_status_code(self, mock_controller):
        mock_controller.get_roles.return_value = {}
        actual = get_roles()

        assert actual.status_code == 200

    def test_get_roles__should_return_success_headers(self, mock_controller):
        mock_controller.get_roles.return_value = {}
        actual = get_roles()

        assert actual.content_type == 'application/json'

    def test_get_roles__should_return_data_from_the_controller(self, mock_controller):
        response = {'roles': ['admin', 'user']}
        mock_controller.get_roles.return_value = response
        actual = get_roles()

        assert json.loads(actual.data) == response

    def test_get_roles_v2__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.get_roles_v2.return_value.to_json.return_value = '{}'
        get_roles_v2()

        mock_controller.get_roles_v2.assert_called_with(self.FAKE_JWT_TOKEN)

    def test_get_roles_v2__should_not_throw_exception_when_no_header(self, mock_controller):
        self.ctx = setup_request(self.app, self.ctx)
        mock_controller.get_roles_v2.return_value.to_json.return_value = '{}'
        get_roles_v2()

        mock_controller.get_roles_v2.assert_called_with(None)

    def test_get_roles_v2__should_return_success_status_code(self, mock_controller):
        mock_controller.get_roles_v2.return_value.to_json.return_value = '{}'
        actual = get_roles_v2()

        assert actual.status_code == 200

    def test_get_roles_v2__should_return_success_headers(self, mock_controller):
        mock_controller.get_roles_v2.return_value.to_json.return_value = '{}'
        actual = get_roles_v2()

        assert actual.content_type == 'application/json'

    def test_get_roles_v2__should_return_data_from_the_controller(self, mock_controller):
        mock_controller.get_roles_v2.return_value.to_json.return_value = '{"roles": ["admin", "user"]}'
        actual = get_roles_v2()

        assert json.loads(actual.data) == {'roles': ['admin', 'user']}


@patch('svc.endpoints.account_routes.account_controller')
class TestChildAccountRoutes:
    USER_ID = '123bac34'
    FAKE_JWT_TOKEN = 'fakeJwtToken'

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = setup_request(self.app, bearer=self.FAKE_JWT_TOKEN)

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
