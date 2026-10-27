import logging
import threading
import time

from svc.config.singleton import Singleton
from svc.constants.home_automation import Garage
from svc.db.repositories.device_repository import DeviceRepository
from svc.utilities import api_utils


@Singleton
class GarageEventBroadcaster:
    def __init__(self):
        self._version = 0
        self._latest_status = None
        self._condition = threading.Condition()

    def start(self):
        thread = threading.Thread(target=self.__listen, daemon=True)
        thread.start()

    def publish(self, status):
        with self._condition:
            self._latest_status = status
            self._version += 1
            self._condition.notify_all()

    def latest(self):
        with self._condition:
            return self._version, self._latest_status

    def wait_for_update(self, seen_version, timeout):
        with self._condition:
            if self._version == seen_version:
                self._condition.wait(timeout)
            if self._version == seen_version:
                return None
            return self._version, self._latest_status

    def consume_upstream(self):
        with DeviceRepository() as database:
            info = database.get_device_info('garage_door')
        url = f'http://{info.ip_address}:{info.ip_port}'
        for status in api_utils.stream_garage_door_events(info.api_key, url):
            self.publish(status)

    def __listen(self):
        while True:
            try:
                self.consume_upstream()
            except Exception as exc:
                logging.warning(f'Garage event stream disconnected: {exc}')
            time.sleep(Garage.STREAM_RECONNECT_SECONDS)
