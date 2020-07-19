import json
import os

import jwt
from mock import patch, ANY

from svc.controllers.app_controller import get_login, get_user_preferences, save_user_preferences, change_password, \
    get_roles, create_child_account_by_user


@patch('svc.controllers.app_controller.UserDatabaseManager')
@patch('svc.controllers.app_controller.jwt_utils')
class TestLoginController:
    BASIC_AUTH_TOKEN = 'not_a_real_auth_token'
    JWT_SECRET = 'fake_jwt_secret'
    BEARER_TOKEN = jwt.encode({}, JWT_SECRET, algorithm='HS256').decode('UTF-8')
    USER = 'user_name'
    PWORD = 'password'
    USER_ID = 'fake_user_id'

    def setup_method(self, _):
        os.environ.update({'JWT_SECRET': self.JWT_SECRET})

    def teardown_method(self, _):
        os.environ.pop('JWT_SECRET')

    def test_get_login__should_call_validate_credentials_with_post_body(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_db.return_value.__enter__.return_value.validate_credentials.assert_called_with(self.USER, self.PWORD)

    def test_get_login__should_call_extract_credentials(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_jwt.extract_credentials.assert_called_with(self.BASIC_AUTH_TOKEN)

    def test_get_login__should_call_create_jwt_token_with_database_response(self, mock_jwt, mock_db):
        user_info = {'user_id': 'sdfasdf', 'role_name': 'lighting'}
        mock_db.return_value.__enter__.return_value.validate_credentials.return_value = user_info
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        get_login(self.BASIC_AUTH_TOKEN)

        mock_jwt.create_jwt_token.assert_called_with(user_info)

    def test_get_login__should_return_response_from_jwt_service(self, mock_jwt, mock_db):
        mock_jwt.extract_credentials.return_value = (self.USER, self.PWORD)
        mock_jwt.create_jwt_token.return_value = self.BEARER_TOKEN
        actual = get_login(self.BASIC_AUTH_TOKEN)

        assert actual == self.BEARER_TOKEN

    def test_get_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BASIC_AUTH_TOKEN)

    def test_get_user_preferences__should_call_get_preferences_by_user(self, mock_jwt, mock_db):
        get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(self.USER_ID)

    def test_get_user_preferences__should_return_preferences_response(self, mock_jwt, mock_db):
        expected_preferences = {'unit': 'imperial', 'city': 'Des Moines'}
        mock_db.return_value.__enter__.return_value.get_preferences_by_user.return_value = expected_preferences

        actual = get_user_preferences(self.BASIC_AUTH_TOKEN, self.USER_ID)

        assert actual == expected_preferences

    def test_save_user_preferences__should_validate_bearer_token(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        request_data = json.dumps({}).encode()

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_jwt.is_jwt_valid.assert_called_with(bearer_token)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_id(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        request_data = json.dumps({}).encode()

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(self.USER_ID, ANY)

    def test_save_user_preferences__should_call_insert_preferences_by_user_with_user_info(self, mock_jwt, mock_db):
        bearer_token = 'fakeBearerToken'
        user_preferences = {'city': 'Berlin'}
        request_data = json.dumps(user_preferences).encode('UTF-8')

        save_user_preferences(bearer_token, self.USER_ID, request_data)

        mock_db.return_value.__enter__.return_value.insert_preferences_by_user.assert_called_with(ANY, user_preferences)

    def test_change_password__should_validate_jwt_token(self, mock_jwt, mock_db):
        request = json.dumps({'userName': None, 'oldPassword': None, 'newPassword': None}).encode('UTF-8')
        change_password(self.BEARER_TOKEN, self.USER_ID, request)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_change_password__should_call_database_change_user_password_with_user_id(self, mock_jwt, mock_db):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(self.USER_ID, ANY, ANY)

    def test_change_password__should_call_database_change_user_password_with_old_password(self, mock_jwt, mock_db):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, self.PWORD, ANY)

    def test_change_password__should_call_database_change_user_password_with_new_password(self, mock_jwt, mock_db):
        new_password = 'new password'
        request = {'userName': self.USER, 'oldPassword': self.PWORD, 'newPassword': new_password}
        change_password(self.BEARER_TOKEN, self.USER_ID, json.dumps(request).encode('UTF-8'))

        mock_db.return_value.__enter__.return_value.change_user_password.assert_called_with(ANY, ANY, new_password)

    def test_get_roles__should_make_call_to_validate_jwt(self, mock_jwt, mock_db):
        get_roles(self.BEARER_TOKEN, self.USER_ID)

        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_get_roles__should_make_call_to_get_roles(self, mock_jwt, mock_db):
        get_roles(self.BEARER_TOKEN, self.USER_ID)

        mock_db.return_value.__enter__.return_value.get_roles_by_user.assert_called_with(self.USER_ID)

    def test_get_roles__should_return_the_result_from_the_database(self, mock_jwt, mock_db):
        roles = {'roles': []}
        mock_db.return_value.__enter__.return_value.get_roles_by_user.return_value = roles
        actual = get_roles(self.BEARER_TOKEN, self.USER_ID)

        assert actual == roles

    def test_create_child_account_by_user__should_validate_bearer_token(self, mock_jwt, mock_db):
        request = json.dumps({'email': '', 'roles': []}).encode()
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_jwt.is_jwt_valid.assert_called_with(self.BEARER_TOKEN)

    def test_create_child_account_by_user__should_make_call_to_database_with_user_id(self, mock_jwt, mock_db):
        request = json.dumps({'email': '', 'roles': []}).encode()
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(self.USER_ID, ANY, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_email(self, mock_jwt, mock_db):
        email = 'thor_thunder@gmail.com'
        request = json.dumps({'email': email, 'roles': []}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, email, ANY, ANY)

    def test_create_child_account_by_user__should_make_call_to_database_with_roles(self, mock_jwt, mock_db):
        roles = ['Im a role!!!']
        request = json.dumps({'email': '', 'roles': roles}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, roles, ANY)

    @patch('svc.controllers.app_controller.generate_password')
    def test_create_child_account_by_user__should_make_call_to_database_with_new_password(self, mock_pass, mock_jwt, mock_db):
        roles = ['Im a role!!!']
        password = 'brandNewPassword'
        mock_pass.return_value = password
        request = json.dumps({'email': '', 'roles': roles}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)
        mock_db.return_value.__enter__.return_value.create_child_account.assert_called_with(ANY, ANY, ANY, password)

    @patch('svc.controllers.app_controller.generate_password')
    @patch('svc.controllers.app_controller.send_new_account_email')
    def test_create_child_account_by_user__should_make_call_to_send_new_account_email(self, mock_api, mock_pass, mock_jwt, mock_db):
        email = 'test@test.com'
        password = 'brandNewPassword'
        mock_pass.return_value = password
        request = json.dumps({'email': email, 'roles': []}).encode('UTF-8')
        create_child_account_by_user(self.BEARER_TOKEN, self.USER_ID, request)

        mock_api.assert_called_with(email, password)
