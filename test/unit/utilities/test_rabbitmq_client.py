import pytest
from mock import patch, call, ANY

from svc.utilities.rabbitmq_client import publish, initialize_queue


@patch('svc.utilities.rabbitmq_client.Settings')
@patch('svc.utilities.rabbitmq_client.pika')
class TestRabbitMqClient:
    QUEUE_NAME = 'home-automation-test'
    EXCHANGE = 'home_automation'

    def __arrange(self, mock_pika, mock_settings):
        mock_settings.get_instance.return_value.Queue.exchange = self.EXCHANGE
        return mock_pika.BlockingConnection.return_value.channel.return_value

    def test_publish__should_declare_queue_before_publishing(self, mock_pika, mock_settings):
        channel = self.__arrange(mock_pika, mock_settings)

        publish(self.QUEUE_NAME, {'action': 'set'})

        assert channel.method_calls[:4] == [
            call.exchange_declare(exchange=self.EXCHANGE, exchange_type='direct', durable=False),
            call.queue_declare(queue=self.QUEUE_NAME, durable=True),
            call.queue_bind(queue=self.QUEUE_NAME, exchange=self.EXCHANGE, routing_key=self.QUEUE_NAME),
            call.basic_publish(exchange=self.EXCHANGE, routing_key=self.QUEUE_NAME, body=b'{"action": "set"}', properties=ANY),
        ]

    def test_publish__should_set_message_expiration_in_milliseconds_when_ttl_given(self, mock_pika, mock_settings):
        self.__arrange(mock_pika, mock_settings)

        publish(self.QUEUE_NAME, {'action': 'toggle'}, 30)

        mock_pika.BasicProperties.assert_called_with(content_type='application/json', delivery_mode=1, expiration='30000')

    def test_publish__should_not_expire_message_when_no_ttl_given(self, mock_pika, mock_settings):
        self.__arrange(mock_pika, mock_settings)

        publish(self.QUEUE_NAME, {'action': 'set'})

        mock_pika.BasicProperties.assert_called_with(content_type='application/json', delivery_mode=1, expiration=None)

    def test_publish__should_close_connection(self, mock_pika, mock_settings):
        self.__arrange(mock_pika, mock_settings)

        publish(self.QUEUE_NAME, {'action': 'set'})

        mock_pika.BlockingConnection.return_value.close.assert_called_once()

    def test_publish__should_raise_when_broker_unavailable(self, mock_pika, mock_settings):
        self.__arrange(mock_pika, mock_settings)
        mock_pika.BlockingConnection.side_effect = Exception('refused')

        with pytest.raises(Exception, match='Broker Unavailable'):
            publish(self.QUEUE_NAME, {'action': 'set'})

    def test_initialize_queue__should_declare_and_bind_queue(self, mock_pika, mock_settings):
        channel = self.__arrange(mock_pika, mock_settings)

        initialize_queue(self.QUEUE_NAME)

        channel.queue_declare.assert_called_once_with(queue=self.QUEUE_NAME, durable=True)
        channel.queue_bind.assert_called_once_with(queue=self.QUEUE_NAME, exchange=self.EXCHANGE, routing_key=self.QUEUE_NAME)

    def test_initialize_queue__should_not_raise_when_broker_unavailable(self, mock_pika, mock_settings):
        self.__arrange(mock_pika, mock_settings)
        mock_pika.BlockingConnection.side_effect = Exception('refused')

        initialize_queue(self.QUEUE_NAME)
