import json
from functools import partial

import pika

from constants.settings_state import Settings
from utilities.event_client import MyThread


class RabbitMQClient:

    def __init__(self, settings: Settings):
        self.settings = settings.Queue
        self.queue_name = 'my_queue'
        self.exchange = 'home_automation'
        self._connection = None
        self._channel = None

    def publish(self, routing_key: str, payload: dict, persistent: bool = False):
        try:
            connection = self._open_connection()
        except Exception as exc:
            raise Exception(f'Broker Unavailable: \n {str(exc)}')
        try:
            channel = connection.channel()
            channel.exchange_declare(exchange=self.exchange, exchange_type='direct', durable=False)
            body = json.dumps(payload).encode('utf-8')
            props = pika.BasicProperties(content_type='application/json', delivery_mode=2 if persistent else 1)
            channel.basic_publish(exchange=self.exchange, routing_key=routing_key, body=body, properties=props)
        finally:
            self._close(connection)

    def start_consumer(self, worker_function):
        t = MyThread.get_instance()
        bound_worker = partial(self._consume, worker_function)
        t.initialize(bound_worker)
        t.start()

    def stop_consumer(self):
        if not self._connection or not self._channel:
            return

        try:
            self._connection.add_callback_threadsafe(lambda: self._channel.stop_consuming())
        except Exception:
            try:
                self._connection.add_callback_threadsafe(lambda: self._connection.close())
            except Exception:
                pass

        t = MyThread.get_instance()
        t.stop()
        try:
            t.join(5)
        except RuntimeError:
            pass

    def _open_connection(self):
        credentials = pika.PlainCredentials(self.settings.user_name, self.settings.password)
        params = pika.ConnectionParameters(host=self.settings.host, port=self.settings.port,
                                           virtual_host=self.settings.vhost, credentials=credentials, socket_timeout=2)
        return pika.BlockingConnection(params)

    def _consume(self, worker_function):
        try:
            self._connection = self._open_connection()
        except Exception as exc:
            raise Exception(f'Broker Unavailable: \n {str(exc)}')
        try:
            self._channel = self._connection.channel()
            self._channel.basic_consume(queue=self.queue_name, on_message_callback=worker_function, auto_ack=False)
            self._channel.start_consuming()
        finally:
            self._close()
            self._connection = None
            self._channel = None

    def _close(self, connection=None):
        try:
            connection.close() if connection else self._connection.close()
        except Exception:
            pass
