import jwt
import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.constants.home_automation import AuthClaims
from svc.controllers.account_controller import change_password, create_child_account_by_user, \
    get_child_accounts_by_user, delete_child_account


@patch('svc.controllers.account_controller.CredentialRepository')
@patch('svc.controllers.account_controller.AuthClient')
class TestAccountCredentials:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER = 'user_name'
    PASSWORD = 'password'
    USER_ID = 'fake_user_id'

    def test_change_password__should_validate_jwt_token(self, mock_jwt, mock_db):
        request = {'userName': None, 'oldPassword': None, 'newPassword': None}
        change_password(self.BEARER_TOKEN, request)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_change_password__should_call_database_change_user_password_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        request = {'userName': self.USER, 'oldPassword': self.PASSWORD, 'newPassword': 'new password'}
        change_password(self.BEARER_TOKEN, request)

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(self.USER_ID, ANY, ANY)

    def test_change_password__should_call_database_change_user_password_with_old_password(self, mock_jwt, mock_db):
        request = {'userName': self.USER, 'oldPassword': self.PASSWORD, 'newPassword': 'new password'}
        change_password(self.BEARER_TOKEN, request)

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, self.PASSWORD, ANY)

    def test_change_password__should_call_database_change_user_password_with_new_password(self, mock_jwt, mock_db):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PASSWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, request)

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, ANY, new_password)


@patch('svc.controllers.account_controller.AccountRepository')
@patch('svc.controllers.account_controller.AuthClient')
class TestAccountRoles:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256')
    USER = 'user_name'
    PASSWORD = 'password'
    USER_ID = 'fake_user_id'

    def test_create_child_account_by_user__should_validate_bearer_token(self, mock_jwt, mock_db):
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_create_child_account_by_user__should_make_call_to_database_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        request = {'email': 'test', 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(self.USER_ID, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_email(self, mock_jwt, mock_db):
        email = 'thor_thunder@gmail.com'
        request = {'email': email, 'deviceIds': ['stuff']}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, email, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_device_ids(self, mock_jwt, mock_db):
        device_ids = ['device']
        request = {'email': 'test', 'deviceIds': device_ids}
        create_child_account_by_user(self.BEARER_TOKEN, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, device_ids)

    def test_create_child_account_by_user__should_raise_bad_request_when_no_email(self, mock_jwt, mock_db):
        request = {'email': '', 'roles': ['sweet ass role']}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_raise_bad_request_when_no_device_ids(self, mock_jwt, mock_db):
        request = {'email': 'test', 'deviceIds': []}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_raise_bad_request_when_device_ids_none(self, mock_jwt, mock_db):
        request = {'email': 'test'}
        with pytest.raises(BadRequest):
            create_child_account_by_user(self.BEARER_TOKEN, request)

    def test_create_child_account_by_user__should_return_response_from_database_method(self, mock_jwt, mock_db):
        request = {'email': 'test', 'deviceIds': ['stuff']}
        response = {'user_data': 'doesnt matter'}
        mock_db.return_value.__enter__.return_value.create_child_account.return_value = response
        actual = create_child_account_by_user(self.BEARER_TOKEN, request)
        assert actual == response

    def test_get_child_accounts_by_user__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_child_accounts_by_user(self.BEARER_TOKEN)

        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_child_accounts_by_user__should_call_database_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        get_child_accounts_by_user(self.BEARER_TOKEN)

        mock_db.return_value.__enter__.return_value.get_user_child_accounts.assert_called_with(self.USER_ID)

    def test_get_child_accounts_by_user__should_return_response_from_database(self, mock_jwt, mock_db):
        response = {'response': 'response data'}
        mock_db.return_value.__enter__.return_value.get_user_child_accounts.return_value = response
        actual = get_child_accounts_by_user(self.BEARER_TOKEN)

        assert actual == response

    def test_delete_child_account__should_validate_bearer_token(self, mock_jwt, mock_db):
        child_user_id = '123asdf'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_jwt.get_instance.return_value.verify_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_delete_child_account__should_call_database_with_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        child_user_id = '123acv'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_db.return_value.__enter__.return_value.delete_child_user_account.assert_called_with(self.USER_ID, ANY)

    def test_delete_child_account__should_call_database_with_child_user_id(self, mock_jwt, mock_db):
        mock_jwt.get_instance.return_value.verify_jwt.return_value = {AuthClaims.USER_ID: self.USER_ID}
        child_user_id = '123basdf'
        delete_child_account(self.BEARER_TOKEN, child_user_id)
        mock_db.return_value.__enter__.return_value.delete_child_user_account.assert_called_with(ANY, child_user_id)