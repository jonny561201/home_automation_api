from mock import patch

from svc.services.auth0_service import provision_account, assign_roles


@patch('svc.services.auth0_service.api_utils')
class TestProvisionAccount:
    EMAIL = 'child@test.com'
    AUTH0_USER_ID = 'auth0|123'
    ROLE_IDS = ['role_1', 'role_2']

    def test_provision_account__should_create_auth0_user_with_email(self, mock_api):
        provision_account(self.EMAIL, self.ROLE_IDS)
        mock_api.create_auth0_user.assert_called_with(self.EMAIL)

    def test_provision_account__should_assign_roles_with_created_user_id_and_role_ids(self, mock_api):
        mock_api.create_auth0_user.return_value = self.AUTH0_USER_ID
        provision_account(self.EMAIL, self.ROLE_IDS)
        mock_api.assign_auth0_roles.assert_called_with(self.AUTH0_USER_ID, self.ROLE_IDS)

    def test_provision_account__should_not_assign_roles_when_role_ids_empty(self, mock_api):
        provision_account(self.EMAIL, [])
        mock_api.assign_auth0_roles.assert_not_called()

    def test_provision_account__should_send_password_reset_with_email(self, mock_api):
        provision_account(self.EMAIL, self.ROLE_IDS)
        mock_api.send_auth0_password_reset.assert_called_with(self.EMAIL)

    def test_provision_account__should_send_password_reset_when_role_ids_empty(self, mock_api):
        provision_account(self.EMAIL, [])
        mock_api.send_auth0_password_reset.assert_called_with(self.EMAIL)


@patch('svc.services.auth0_service.api_utils')
class TestAssignRoles:
    AUTH0_ID = 'auth0|fake_user'
    ROLE_IDS = ['rol_abc', 'rol_def']

    def test_assign_roles__should_call_assign_auth0_roles_with_auth0_id_and_role_ids(self, mock_api):
        assign_roles(self.AUTH0_ID, self.ROLE_IDS)
        mock_api.assign_auth0_roles.assert_called_with(self.AUTH0_ID, self.ROLE_IDS)

    def test_assign_roles__should_not_call_assign_auth0_roles_when_role_ids_empty(self, mock_api):
        assign_roles(self.AUTH0_ID, [])
        mock_api.assign_auth0_roles.assert_not_called()
