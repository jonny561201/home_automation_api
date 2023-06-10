import pytest
from mock import patch, ANY
from werkzeug.exceptions import BadRequest

from svc.constants.settings_state import Settings
from svc.controllers.light_controller import get_assigned_light_groups, set_assigned_light_groups, set_assigned_light


@patch('svc.controllers.light_controller.Settings')
@patch('svc.controllers.light_controller.is_jwt_valid')
@patch('svc.controllers.light_controller.api_utils')
class TestLightRequest:
    LIGHT_USERNAME = 'fakeUsername'
    LIGHT_PASSWORD = 'fakePassword'
    API_KEY = "fakeApiKey"
    BEARER_TOKEN = "EAK#K$%B$#K#"
    GROUP_ID = '1'
    STATE = False

    def setup_method(self):
        self.REQUEST = {'on': self.STATE, 'groupId': self.GROUP_ID}
        self.SETTINGS = Settings.get_instance()
        self.SETTINGS.dev_mode = True
        self.SETTINGS.settings = {'lightApiKey': self.API_KEY}

    def test_set_assigned_light_groups__should_call_is_jwt_valid(self, mock_api, mock_jwt, mock_setting):
        set_assigned_light_groups(self.BEARER_TOKEN, self.REQUEST)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_assigned_light_groups__should_make_api_call_to_set_state(self, mock_api, mock_jwt, mock_setting):
        mock_setting.get_instance.return_value = self.SETTINGS
        set_assigned_light_groups(self.BEARER_TOKEN, self.REQUEST)

        mock_api.set_light_groups.assert_called_with(self.API_KEY, self.GROUP_ID, self.STATE, None)

    def test_set_assigned_light_groups__should_make_api_call_to_set_brightness_optionally(self, mock_api, mock_jwt, mock_setting):
        brightness = 255
        self.REQUEST['brightness'] = brightness
        set_assigned_light_groups(self.BEARER_TOKEN, self.REQUEST)

        mock_api.set_light_groups.assert_called_with(ANY, ANY, ANY, brightness)

    def test_set_assigned_light_groups__should_call_api_utils_with_on_property(self, mock_api, mock_jwt, mock_setting):
        set_assigned_light_groups(self.BEARER_TOKEN, self.REQUEST)

        mock_api.set_light_groups.assert_called_with(ANY, ANY, self.STATE, None)

    def test_set_assigned_light_groups__should_raise_bad_request_when_group_id_not_supplied(self, mock_api, mock_jwt, mock_setting):
        request = {'on': False}
        with pytest.raises(BadRequest):
            set_assigned_light_groups(self.BEARER_TOKEN, request)

    def test_set_assigned_light_groups__should_raise_bad_request_when_on_not_supplied(self, mock_api, mock_jwt, mock_setting):
        request = {'groupId': False}
        with pytest.raises(BadRequest):
            set_assigned_light_groups(self.BEARER_TOKEN, request)

    def test_set_assigned_light__should_call_is_jwt_valid(self, mock_api, mock_jwt, mock_setting):
        request_data = {'lightId': '4', 'on': True, 'brightness': 179}
        set_assigned_light(self.BEARER_TOKEN, request_data)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_set_assigned_light__should_make_call_to_set_light_state(self, mock_api, mock_jwt, mock_setting):
        light_id = '2'
        brightness = 65
        request_data = {'lightId': light_id, 'on': True, 'brightness': brightness}
        mock_setting.get_instance.return_value = self.SETTINGS
        set_assigned_light(self.BEARER_TOKEN, request_data)

        mock_api.set_light_state.assert_called_with(self.API_KEY, light_id, brightness)

    def test_get_assigned_light_groups__should_call_is_jwt_valid(self, mock_api, mock_jwt, mock_setting):
        mock_setting.get_instance.return_value = self.SETTINGS
        get_assigned_light_groups(self.BEARER_TOKEN)

        mock_jwt.assert_called_with(self.BEARER_TOKEN)

    def test_get_assigned_light_groups__should_make_api_call_to_get_full_state(self, mock_api, mock_jwt, mock_setting):
        mock_setting.get_instance.return_value = self.SETTINGS
        get_assigned_light_groups(self.BEARER_TOKEN)

        mock_api.get_light_groups.assert_called_with(self.API_KEY)
