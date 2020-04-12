from svc.manager import create_app


class TestDeviceRoutesIntegration:
    TEST_CLIENT = None
    USER_ID = '1234abcd'

    def setup_method(self):
        flask_app = create_app('__main__')
        self.TEST_CLIENT = flask_app.test_client()

    def test_add_device_by_user_id__should_return_unauthorized(self):
        post_body = '{}'
        actual = self.TEST_CLIENT.post('userId/' + self.USER_ID + '/devices', headers={}, data=post_body)
        assert actual.status_code == 401
