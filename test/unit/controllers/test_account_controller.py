import jwt
import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.controllers.account_controller import create_child_account_by_user, get_child_accounts_by_user, delete_child_account


@patch('svc.controllers.account_controller.api_utils')
@patch('svc.controllers.account_controller.DeviceRepository')
@patch('svc.controllers.account_controller.AccountRepository')
@patch('svc.controllers.account_controller.AuthClient')
class TestAccountRoles:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER = 'user_name'
    PASSWORD = 'password'
    USER_ID = 'fake_user_id'

    def test_create_child_account_by_user__should_validate_bearer_token(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_create_child_account_by_user__should_make_call_to_database_with_user_id(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_account_db.return_value.__enter__.return_value.create_child_account.assert_called_with(self.USER_ID, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_email(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        email = 'thor_thunder@gmail.com'
        request = {'email': email, 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_account_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, email, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_device_ids(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        device_ids = ['device']
        request = {'email': 'test', 'deviceIds': device_ids}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_account_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, device_ids)

    def test_create_child_account_by_user__should_raise_bad_request_when_no_email(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        request = {'email': '', 'deviceIds': ['stuff']}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_raise_bad_request_when_no_device_ids(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        request = {'email': 'test', 'deviceIds': []}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_raise_bad_request_when_device_ids_none(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        request = {'email': 'test'}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_return_response_from_database_method(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        request = {'email': 'test', 'deviceIds': ['stuff']}
        response = {'user_data': 'doesnt matter'}
        mock_account_db.return_value.__enter__.return_value.create_child_account.return_value = response
        actual = create_child_account_by_user(self.BEARER_TOKEN, request)
        assert actual == response

    def test_create_child_account_by_user__should_query_role_ids_from_device_repository(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        device_ids = ['device_1', 'device_2']
        request = {'email': 'test', 'deviceIds': device_ids}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_device_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.assert_called_with(self.USER_ID, device_ids)

    def test_create_child_account_by_user__should_create_auth0_user_with_email(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        email = 'child@test.com'
        request = {'email': email, 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_api.create_auth0_user.assert_called_with(email)

    def test_create_child_account_by_user__should_assign_auth0_roles_with_db_role_ids(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        role_ids = ['role_1', 'role_2']
        mock_device_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.return_value = role_ids
        mock_api.create_auth0_user.return_value = 'auth0|123'
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_api.assign_auth0_roles.assert_called_with('auth0|123', role_ids)

    def test_create_child_account_by_user__should_not_assign_roles_when_empty(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_device_db.return_value.__enter__.return_value.get_role_ids_by_device_ids.return_value = []
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_api.assign_auth0_roles.assert_not_called()

    def test_create_child_account_by_user__should_send_password_reset_email(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        email = 'child@test.com'
        request = {'email': email, 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_api.send_auth0_password_reset.assert_called_with(email)

    def test_get_child_accounts_by_user__should_validate_bearer_token(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        get_child_accounts_by_user(self.BEARER_TOKEN)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_child_accounts_by_user__should_call_database_with_user_id(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        get_child_accounts_by_user(self.BEARER_TOKEN)
        mock_account_db.return_value.__enter__.return_value.get_user_child_accounts.assert_called_with(self.USER_ID)

    def test_get_child_accounts_by_user__should_return_response_from_database(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        response = {'response': 'response data'}
        mock_account_db.return_value.__enter__.return_value.get_user_child_accounts.return_value = response
        actual = get_child_accounts_by_user(self.BEARER_TOKEN)
        assert actual == response

    def test_delete_child_account__should_validate_bearer_token(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        child_user_id = '123asdf'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_delete_child_account__should_call_database_with_user_id(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        child_user_id = '123acv'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_account_db.return_value.__enter__.return_value.delete_child_user_account.assert_called_with(self.USER_ID, ANY)

    def test_delete_child_account__should_call_database_with_child_user_id(self, mock_jwt, mock_account_db, mock_device_db, mock_api):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        child_user_id = '123basdf'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_account_db.return_value.__enter__.return_value.delete_child_user_account.assert_called_with(ANY, child_user_id)
