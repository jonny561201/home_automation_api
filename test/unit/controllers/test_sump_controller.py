import json
import uuid

from mock import patch

from models.sump import SumpLevel
from svc.controllers.sump_controller import get_sump_level, save_current_level


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_call_get_current_sump_level_by_user(mock_database, mock_jwt):
    user_id = uuid.uuid4().hex
    bearer_token = 'abdsadf2345'
    get_sump_level(user_id, bearer_token)

    mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.assert_called_with(user_id)


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_return_response_with_distance(mock_database, mock_jwt):
    distance = 3.14159
    bearer_token = 'asdflkhsad98778236'
    user_id = 'fake12354'
    mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = {'is_imperial': False}
    mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': distance, 'warningLevel': 0}
    mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': distance, 'testItem': 123}

    actual = get_sump_level(user_id, bearer_token)

    assert actual == SumpLevel(currentDepth=distance, depthUnit='cm', warningLevel=0, averageDepth=distance)


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_return_response_with_distance_converted_to_imperial(mock_database, mock_jwt):
    current_distance = 2.54
    average_distance = 5.08
    bearer_token = 'asdflkhsad98778236'
    user_id = 'fake12354'
    mock_database.return_value.__enter__.return_value.get_preferences_by_user.return_value = {'is_imperial': True}
    mock_database.return_value.__enter__.return_value.get_current_sump_level_by_user.return_value = {'currentDepth': current_distance, 'warningLevel': 0}
    mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.return_value = {'averageDepth': average_distance, 'testItem': 123}

    actual = get_sump_level(user_id, bearer_token)

    assert actual == SumpLevel(currentDepth=1.0, depthUnit='in', warningLevel=0, averageDepth=2.0)


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_call_is_jwt_valid(mock_database, mock_jwt):
    user_id = 'fake1234'
    bearer_token = 'lkhasdhlufiou0892390784'

    get_sump_level(user_id, bearer_token)

    mock_jwt.assert_called_with(bearer_token)


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_call_get_preferences_by_user(mock_database, mock_jwt):
    user_id = 'fake1234'
    bearer_token = 'lkhasdhlufiou0892390784'

    get_sump_level(user_id, bearer_token)

    mock_database.return_value.__enter__.return_value.get_preferences_by_user.assert_called_with(user_id)


@patch('svc.controllers.sump_controller.is_jwt_valid')
@patch('svc.controllers.sump_controller.UserDatabaseManager')
def test_get_sump_level__should_call_get_average_sump_level_by_user(mock_database, mock_jwt):
    user_id = 'fake1234'
    bearer_token = 'lkhasdhlufiou0892390784'

    get_sump_level(user_id, bearer_token)

    mock_database.return_value.__enter__.return_value.get_average_sump_level_by_user.assert_called_with(user_id)


@patch('svc.controllers.sump_controller.UserDatabaseManager')
@patch('svc.controllers.sump_controller.is_jwt_valid')
def test_save_current_level__should_call_is_jwt_valid(mock_jwt, mock_db):
    user_id = 1234
    bearer_token = 'fake_token'
    request = json.dumps({'depth': 'test'})

    save_current_level(user_id, bearer_token, request)

    mock_jwt.assert_called_with(bearer_token)


@patch('svc.controllers.sump_controller.UserDatabaseManager')
@patch('svc.controllers.sump_controller.is_jwt_valid')
def test_save_current_level__should_call_save_current_sump_level(mock_jwt, mock_db):
    user_id = 1234
    bearer_token = 'fake_token'
    depth_info = {'depth': 'test'}
    request = json.dumps(depth_info)

    save_current_level(user_id, bearer_token, request)

    mock_db.return_value.__enter__.return_value.insert_current_sump_level.assert_called_with(user_id, depth_info)
