import json

import jwt
from mock import patch, ANY

from svc.controllers.account_controller import change_password, get_roles, create_child_account_by_user, \
    get_child_accounts_by_user


@patch('svc.controllers.account_controller.send_new_account_email')
@patch('svc.controllers.account_controller.UserDatabaseManager')
@patch('svc.controllers.account_controller.jwt_utils')
class TestAccountController:
    BEARER_TOKEN = jwt.encode({}, 'fake_jwt_secret', algorithm='HS256').decode('UTF-8')
    USER = 'user_name'
    PWORD = 'password'
    USER_ID = 'fake_user_id'

    def test_change_password__should_validate_jwt_token(self, mock_jwt, mock_db, mock_email):
        request = json.dumps({'userName': None, 'oldPassword': None, 'newPassword': None}).encode('UTF-8')
        change_password(self.BEARER_TOKEN, self.USER_ID, request)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_change_password__should_call_database_change_user_password_with_user_id(self, mock_jwt, mock_db, mock_email):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(self.USER_ID, ANY, ANY)

    def test_change_password__should_call_database_change_user_password_with_old_password(self, mock_jwt, mock_db, mock_email):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, self.PWORD, ANY)

    def test_change_password__should_call_database_change_user_password_with_new_password(self, mock_jwt, mock_db, mock_email):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, ANY, new_password)

    def test_get_roles__should_make_call_to_validate_jwt(self, mock_jwt, mock_db, mock_email):
        get_roles(self.BEARER_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_roles__should_make_call_to_get_roles(self, mock_jwt, mock_db, mock_email):
        get_roles(self.BEARER_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_roles_by_user.assert_called_with(self.USER_ID)

    def test_get_roles__should_return_the_result_from_the_database(self, mock_jwt, mock_db, mock_email):
        roles = {'roles': []}
        mock_db.return_value.__enter__.return_value.get_roles_by_user.return_value = roles
        actual = get_roles(self.BEARER_TOKEN, self.USER_ID)

        assert actual == roles

    def test_create_child_account_by_user__should_validate_bearer_token(self, mock_jwt, mock_db, mock_email):
        request = json.dumps({'email': '', 'roles': []}).encode()
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_create_child_account_by_user__should_make_call_to_database_with_user_id(self, mock_jwt, mock_db, mock_email):
        request = json.dumps({'email': '', 'roles': []}).encode()
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(self.USER_ID, ANY, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_email(self, mock_jwt, mock_db, mock_email):
        email = 'thor_thunder@gmail.com'
        request = json.dumps({'email': email, 'roles': []}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, email, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_roles(self, mock_jwt, mock_db, mock_email):
        roles = ['Im a role!!!']
        request = json.dumps({'email': '', 'roles': roles}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, roles, ANY)

    @patch('svc.controllers.account_controller.generate_password')
    def test_create_child_account_by_user__should_make_call_to_database_with_new_password(self, mock_pass, mock_jwt, mock_db, mock_email):
        roles = ['Im a role!!!']
        password = 'brandNewPassword'
        mock_pass.return_value = password
        request = json.dumps({'email': '', 'roles': roles}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, ANY, password)

    @patch('svc.controllers.account_controller.generate_password')
    def test_create_child_account_by_user__should_make_call_to_send_new_account_email(self, mock_pass, mock_jwt, mock_db, mock_email):
        email = 'test@test.com'
        password = 'brandNewPassword'
        mock_pass.return_value = password
        request = json.dumps({'email': email, 'roles': []}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)

        mock_email.assert_called_with(email, password)

    def test_get_child_accounts_by_user__should_validate_bearer_token(self, mock_jwt, mock_db, mock_email):
        get_child_accounts_by_user(self.BEARER_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_child_accounts_by_user__should_call_database_with_user_id(self, mock_jwt, mock_db, mock_email):
        get_child_accounts_by_user(self.BEARER_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_user_child_accounts.assert_called_with(self.USER_ID)

    def test_get_child_accounts_by_user__should_return_response_from_database(self, mock_jwt, mock_db, mock_email):
        response = {'response': 'response data'}
        mock_db.return_value.__enter__.return_value.get_user_child_accounts.return_value = response
        actual = get_child_accounts_by_user(self.BEARER_TOKEN, self.USER_ID)

        assert actual == response
