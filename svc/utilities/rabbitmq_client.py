import json

import pika

from svc.config.settings_state import Settings, Queue


def initialize_queue(queue_name: str):
    settings = Settings.get_instance().Queue

    connection = None
    try:
        connection = _open_connection(settings)
        channel = connection.channel()
        channel.exchange_declare(exchange=settings.exchange, exchange_type='direct', durable=False)
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(queue=queue_name, exchange=settings.exchange, routing_key=queue_name)
    finally:
        try:
            connection.close()
        except Exception:
            pass


def publish(queue_name: str, payload: dict):
    settings = Settings.get_instance().Queue

    try:
        connection = _open_connection(settings)
    except Exception as exc:
        raise Exception(f'Broker Unavailable: \n {str(exc)}')
    try:
        channel = connection.channel()
        body = json.dumps(payload).encode('utf-8')
        props = pika.BasicProperties(content_type='application/json', delivery_mode=1)
        channel.basic_publish(exchange=settings.exchange, routing_key=queue_name, body=body, properties=props)
    finally:
        try:
            connection.close()
        except Exception:
            pass


def _open_connection(settings: Queue):
    credentials = pika.PlainCredentials(settings.user_name, settings.password)
    params = pika.ConnectionParameters(host=settings.host, port=settings.port, virtual_host=settings.vhost, credentials=credentials, socket_timeout=2)

    return pika.BlockingConnection(params)
