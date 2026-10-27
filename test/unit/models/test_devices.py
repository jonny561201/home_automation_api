from svc.models.devices import DeviceInfo


def test_base_url__should_build_http_url_from_ip_and_port():
    info = DeviceInfo(id='device-1', ip_address='192.168.1.20', ip_port=5001, api_key='fake-api-key')

    assert info.base_url == 'http://192.168.1.20:5001'
