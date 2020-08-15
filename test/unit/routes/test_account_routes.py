import json

import pytest
from mock import patch, ANY
from werkzeug.exceptions import Unauthorized

from svc.routes.account_routes import update_user_password, post_child_account_by_user, get_child_accounts_by_user_id, \
    get_roles_by_user_id


@patch('svc.routes.account_routes.request')
@patch('svc.routes.account_routes.app_controller')
class TestAppRoutes:
    USER_ID = '123bac34'
    FAKE_JWT_TOKEN = 'fakeJwtToken'.encode('UTF-8')

    def test_update_user_password__should_call_change_password_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_update_user_password__should_call_change_password_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(ANY, self.USER_ID, ANY)

    def test_update_user_password__should_call_change_password_controller_with_data(self, mock_controller, mock_request):
        request_data = {'fakeData': 'doesnt matter'}
        mock_request.data = request_data
        update_user_password(self.USER_ID)

        mock_controller.change_password.assert_called_with(ANY, ANY, request_data)

    def test_update_user_password__should_return_success_status_code(self, mock_controller, mock_request):
        actual = update_user_password(self.USER_ID)

        assert actual.status_code == 200

    def test_update_user_password__should_return_success_content(self, mock_controller, mock_request):
        actual = update_user_password(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_post_child_account_by_user__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        post_child_account_by_user(self.USER_ID)
        mock_controller.create_child_account_by_user.assert_called_with(self.FAKE_JWT_TOKEN, ANY, ANY)

    def test_post_child_account_by_user__not_raise_error_when_no_authorization_header(self, mock_controller, mock_request):
        mock_request.headers = {}
        post_child_account_by_user(self.USER_ID)
        mock_controller.create_child_account_by_user.assert_called_with(None, ANY, ANY)

    def test_post_child_account_by_user__should_call_controller_with_user_id(self, mock_controller, mock_request):
        post_child_account_by_user(self.USER_ID)
        mock_controller.create_child_account_by_user.assert_called_with(ANY, self.USER_ID, ANY)

    def test_post_child_account_by_user__should_call_controller_with_post_body(self, mock_controller, mock_request):
        request = {'fake': 'request'}
        mock_request.data = request
        post_child_account_by_user(self.USER_ID)
        mock_controller.create_child_account_by_user.assert_called_with(ANY, ANY, request)

    def test_post_child_account_by_user__should_return_success_status_code(self, mock_controller, mock_request):
        actual = post_child_account_by_user(self.USER_ID)
        assert actual.status_code == 200

    def test_post_child_account_by_user__should_return_success_headers(self, mock_controller, mock_request):
        actual = post_child_account_by_user(self.USER_ID)
        assert actual.content_type == 'text/json'

    def test_get_child_accounts_by_user_id__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.get_child_accounts_by_user.return_value = {}
        get_child_accounts_by_user_id(self.USER_ID)
        mock_controller.get_child_accounts_by_user.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_get_child_accounts_by_user_id__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.get_child_accounts_by_user.return_value = {}
        get_child_accounts_by_user_id(self.USER_ID)
        mock_controller.get_child_accounts_by_user.assert_called_with(ANY, self.USER_ID)

    def test_get_child_accounts_by_user_id__should_return_success_status_code(self, mock_controller, mock_request):
        mock_controller.get_child_accounts_by_user.return_value = {}
        actual = get_child_accounts_by_user_id(self.USER_ID)
        assert actual.status_code == 200

    def test_get_child_accounts_by_user_id__should_return_success_headers(self, mock_controller, mock_request):
        mock_controller.get_child_accounts_by_user.return_value = {}
        actual = get_child_accounts_by_user_id(self.USER_ID)
        assert actual.content_type == 'text/json'

    def test_get_child_accounts_by_user_id__should_return_response_from_controller(self, mock_controller, mock_request):
        response = {'test': 'test data'}
        mock_controller.get_child_accounts_by_user.return_value = response
        actual = get_child_accounts_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == response

    def test_get_child_accounts_by_user_id__should_not_throw_exception_when_no_bearer_token(self, mock_controller, mock_request):
        mock_controller.get_child_accounts_by_user.side_effect = Unauthorized()
        with pytest.raises(Unauthorized):
            get_child_accounts_by_user_id(self.USER_ID)

    def test_get_roles_by_user_id__should_call_controller_with_bearer_token(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.get_roles.return_value = {}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(self.FAKE_JWT_TOKEN, ANY)

    def test_get_roles_by_user_id__should_call_controller_with_user_id(self, mock_controller, mock_request):
        mock_request.headers = {'Authorization': self.FAKE_JWT_TOKEN}
        mock_controller.get_roles.return_value = {}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(ANY, self.USER_ID)

    def test_get_roles_by_user_id__should_not_throw_exception_when_no_header(self, mock_controller, mock_request):
        mock_request.headers = {}
        mock_controller.get_roles.return_value = {}
        get_roles_by_user_id(self.USER_ID)

        mock_controller.get_roles.assert_called_with(None, ANY)

    def test_get_roles_by_user_id__should_return_success_status_code(self, mock_controller, mock_request):
        mock_controller.get_roles.return_value = {}
        actual = get_roles_by_user_id(self.USER_ID)

        assert actual.status_code == 200

    def test_get_roles_by_user_id__should_return_success_headers(self, mock_controller, mock_request):
        mock_controller.get_roles.return_value = {}
        actual = get_roles_by_user_id(self.USER_ID)

        assert actual.content_type == 'text/json'

    def test_get_roles_by_user_id__should_return_data_from_the_controller(self, mock_controller, mock_request):
        response = {'data': 'doesnt matter'}
        mock_controller.get_roles.return_value = response
        actual = get_roles_by_user_id(self.USER_ID)

        assert json.loads(actual.data) == response