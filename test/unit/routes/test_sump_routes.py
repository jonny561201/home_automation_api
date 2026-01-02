import json

from mock import patch

from svc.endpoints.sump_routes import get_current_sump_level, save_current_level_by_user


@patch('svc.endpoints.sump_routes.request')
@patch('svc.endpoints.sump_routes.get_sump_level')
def test_get_current_sump_level__should_call_controller(mock_controller, mock_request):
    bearer_token = 'test123'
    mock_request.headers = {'Authorization': bearer_token}
    user_id = 'fakeuserid'
    mock_controller.return_value = {'fake': 123}

    get_current_sump_level(user_id)

    mock_controller.assert_called_with(user_id, bearer_token)


@patch('svc.endpoints.sump_routes.request')
@patch('svc.endpoints.sump_routes.get_sump_level')
def test_get_current_sump_level__should_return_valid_response(mock_controller, mock_request):
    user_id = 'fakeuserid'
    expected_depth = {'currentDepth': 1234}
    mock_controller.return_value = expected_depth

    actual = get_current_sump_level(user_id)
    json_actual = json.loads(actual.data)

    assert json_actual == expected_depth


@patch('svc.endpoints.sump_routes.request')
@patch('svc.endpoints.sump_routes.get_sump_level')
def test_get_current_sump_level__should_return_success_status(mock_controller, mock_request):
    user_id = 'fakeuserid'
    expected_depth = {'currentDepth': 1234}
    mock_controller.return_value = expected_depth

    actual = get_current_sump_level(user_id)

    assert actual.status_code == 200


@patch('svc.endpoints.sump_routes.request')
@patch('svc.endpoints.sump_routes.save_current_level')
def test_save_current_level_by_user__should_call_controller(mock_controller, mock_request):
    user_id = 1234
    request_body = {}
    bearer_token = 'fake_token'
    mock_request.data = request_body
    mock_request.headers = {'Authorization': bearer_token}

    save_current_level_by_user(user_id)

    mock_controller.assert_called_with(user_id, bearer_token, request_body)
