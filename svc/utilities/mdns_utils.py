from zeroconf import ServiceListener, Zeroconf, ServiceBrowser

from controllers.registration_controller import register_sump_pump
from svc.controllers.registration_controller import register_garage_door


class MdnsListener(ServiceListener):
    SERVICE_TYPE = '_http._tcp.local.'

    def __init__(self):
        self._zeroconf = None
        self._browser = None

    def start(self):
        self._zeroconf = Zeroconf()
        self._browser = ServiceBrowser(self._zeroconf, self.SERVICE_TYPE, self)

    def stop(self):
        if self._zeroconf is not None:
            self._zeroconf.close()
            self._zeroconf = None
            self._browser = None

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info is None:
            return
        service_name = info.properties.get(b'service', b'').decode()
        if service_name == 'garage-door':
            ip = info.parsed_addresses()[0]
            port = info.port
            max_nodes = int(info.properties.get(b'max_nodes', b'1'))
            register_garage_door(service_name, ip, port, max_nodes)

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass