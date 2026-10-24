from flask import Flask
from mock import patch

from svc.endpoints.garage_event_routes import stream_garage_door_status


@patch('svc.endpoints.garage_event_routes.garage_door_controller')
class TestGarageEventRoutes:
    JWT_TOKEN = 'fake-bearer-token'

    def setup_method(self):
        self.app = Flask(__name__)
        self.ctx = self.app.test_request_context(headers={'Authorization': self.JWT_TOKEN})
        self.ctx.push()

    def teardown_method(self):
        self.ctx.pop()

    def test_stream_garage_door_status__should_call_controller_with_bearer_token(self, mock_controller):
        mock_controller.stream_status.return_value = iter([])

        stream_garage_door_status()

        mock_controller.stream_status.assert_called_with(self.JWT_TOKEN)

    def test_stream_garage_door_status__should_return_event_stream(self, mock_controller):
        mock_controller.stream_status.return_value = iter([])

        actual = stream_garage_door_status()

        assert actual.status_code == 200
        assert actual.mimetype == 'text/event-stream'

    def test_stream_garage_door_status__should_disable_caching_and_proxy_buffering(self, mock_controller):
        mock_controller.stream_status.return_value = iter([])

        actual = stream_garage_door_status()

        assert actual.headers['Cache-Control'] == 'no-cache'
        assert actual.headers['X-Accel-Buffering'] == 'no'

    def test_stream_garage_door_status__should_stream_controller_events(self, mock_controller):
        mock_controller.stream_status.return_value = iter([': ping\n\n'])

        actual = stream_garage_door_status()

        assert actual.get_data() == b': ping\n\n'
