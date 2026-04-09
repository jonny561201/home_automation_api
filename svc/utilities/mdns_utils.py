from zeroconf import ServiceListener, Zeroconf, ServiceBrowser

from svc.controllers.devices_controller import register_device


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
        if service_name:
            ip = info.parsed_addresses()[0]
            port = info.port
            register_device(service_name, ip, port)

    def remove_service(self, zc, type_, name):
        pass

    def update_service(self, zc, type_, name):
        pass