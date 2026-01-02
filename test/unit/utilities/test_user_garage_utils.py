from mock import patch

from svc.utilities.user_garage_utils import get_garage_url_by_user


@patch('svc.utilities.user_garage_utils.UserDatabaseManager')
def test_get_garage_url_by_user__should_call_database_when_settings_cannot_be_found(mock_db):
    user_id = 'heyImAUserId'
    get_garage_url_by_user(user_id)

    mock_db.return_value.__enter__.return_value.get_user_garage_ip.assert_called_with(user_id)

@patch('svc.utilities.user_garage_utils.UserDatabaseManager')
def test_get_garage_url_by_user__should_return_url_with_ip_from_database(mock_db):
    user_id = 'heyImAUserId'
    database_response = '1.1.1.1'
    mock_db.return_value.__enter__.return_value.get_user_garage_ip.return_value = database_response
    actual = get_garage_url_by_user(user_id)

    assert actual == f'http://{database_response}'
